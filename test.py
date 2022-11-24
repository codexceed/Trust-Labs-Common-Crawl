from warcio.archiveiterator import ArchiveIterator
import re
import requests
import bs4

if __name__ == "__main__":
    common_crawl_base = "https://data.commoncrawl.org/"
    with open("warc_2020_all.txt", "r") as f:
        warc_files = f.readlines()

    # Regex for precisely spotting variations of "covid-19" and "economy" in the html contents
    regex = re.compile(r"(?i)(?=.*(\.|\s|^)covid(\-*19)?)(?=.*(\.|\s|^)econom(y|ic(al)*|ies)).*")

    valid_urls = []
    for file_url in warc_files:
        entries = 0
        matching_entries = 0
        hits = 0

        file_name = common_crawl_base + file_url.rstrip("\n")

        stream = None
        if file_name.startswith("http://") or file_name.startswith("https://"):
            stream = requests.get(file_name, stream=True).raw
        else:
            raise Exception(f"Invalid URL: {file_name}")

        for record in ArchiveIterator(stream):
            if record.rec_type == "response":
                contents = record.content_stream().read().decode("utf-8", "replace")
                soup = bs4.BeautifulSoup(contents, "html.parser")
                results = soup.find(string=regex, recursive=True)
                if results is not None:
                    print(record.rec_headers.get_header("WARC-Target-URI"))
                    valid_urls.append(record.rec_headers.get_header("WARC-Target-URI"))

        with open("covid_economy_urls_2020.txt", "w") as f:
            f.writelines([url + "\n" for url in valid_urls])