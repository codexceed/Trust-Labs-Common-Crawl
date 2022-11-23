import boto3
import re

if __name__ == "__main__":
    access_key = input("Please provide your AWS access key:")
    secret_key = input("Please provide your AWS secret key:")

    if not (access_key and secret_key):
        access_key, secret_key = None, None

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    s3 = session.resource("s3")
    bucket = s3.Bucket("commoncrawl")

    objects = bucket.objects.filter(Prefix="crawl-data/CC-MAIN-2020")

    warc_files = []
    for obj in objects:
        if re.match(r"^.+\.warc\.gz$", obj.key):
            warc_files.append(obj.key + "\n")

    with open("warc_2020_all.txt", "w") as f:
        f.writelines(warc_files)
