import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from multiprocessing import Manager
from queue import Queue
from typing import List

import requests
from warcio.archiveiterator import ArchiveIterator

# Regex for precisely spotting variations of "covid-19" and "economy" in the html contents
REGEX1 = re.compile(r"(?i)(?=.*(\.|\s|^)covid(\-*19)?).*")
REGEX2 = re.compile(r"(?i)(?=.*(\.|\s|^)econom(y|ic(al)*|ies)).*")
NUM_WORKERS = 6
COMMON_CRAWL_BASE = "https://data.commoncrawl.org/"
ARCHIVE_TIMEOUT_MINS = 15


def queue_archive_uri(file_urls: List[str], queue: Queue) -> None:
    for i, url in enumerate(file_urls):
        print(f"Inserting archive {url} into queue.")
        queue.put((url, i))


def scrape_archive(queue: Queue) -> None:
    while True:
        try:
            start = datetime.now()
            checkpoint = start
            file_url, idx = queue.get(timeout=3)
            print(f"Iterating over archive: {file_url}")
            file_name = COMMON_CRAWL_BASE + file_url.rstrip("\n")
            valid_urls = []
            if file_name.startswith("http://") or file_name.startswith("https://"):
                stream = requests.get(file_name, stream=True).raw
            else:
                raise Exception(f"Invalid URL: {file_name}")

            num_records = 0
            aborted = False
            for record in ArchiveIterator(stream):
                if record.rec_type == "response":
                    contents = record.content_stream().read().decode("utf-8", "replace")
                    if REGEX1.search(contents) and REGEX2.search(contents):
                        print(record.rec_headers.get_header("WARC-Target-URI"))
                        valid_urls.append(record.rec_headers.get_header("WARC-Target-URI"))

                num_records += 1

                if num_records % 100 == 0:
                    time_since_last_checkpoint = datetime.now() - checkpoint
                    time_on_archive = datetime.now() - start
                    print(f"Analyzed {num_records} records on {file_url} at index: {idx}.")
                    print(f"Time since last checkpoint: {time_since_last_checkpoint}")
                    checkpoint = datetime.now()
                    if time_on_archive > timedelta(minutes=ARCHIVE_TIMEOUT_MINS):
                        print(f"Archive at {file_url} (idx: {idx}) being analyzed for too long. Skipping.")
                        aborted = True
                        break

            if valid_urls:
                with open("covid_economy_urls_2020.txt", "a") as f:
                    f.writelines(["\n" + url for url in valid_urls])

            if not aborted:
                with open("processed_files.txt", "a") as f:
                    f.write(f"\n{file_url}")

        except queue.Empty:
            print("No more items in queue. Shutting down worker.")
            break
        else:
            print(f"Finished analyzing archive at {file_url} (idx: {idx}).")


if __name__ == "__main__":
    with open("warc_2020_all.txt", "r") as f:
        warc_files = f.readlines()

    try:
        with open("processed_files.txt", "r") as f:
            processed_files = f.readlines()
    except FileNotFoundError:
        processed_files = []

    target_files = set(warc_files).difference(set(processed_files))
    with ProcessPoolExecutor() as executor:
        manager = Manager()
        file_queue = manager.Queue(8)

        executor.submit(queue_archive_uri, target_files, file_queue)
        executor.map(
            scrape_archive,
            [file_queue for _ in range(NUM_WORKERS)],
        )
        executor.shutdown()
