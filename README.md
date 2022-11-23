# Trust Lab Take-Home: Common Crawl
## Problem Statement
In this task, your goal is to find pages from the common crawl archive that discuss or are
relevant to COVID-19’s economic impact. We would like you to produce a list of 1000 pages
(URL’s) from the 2020 archives that discuss or are relevant to COVID-19’s economic impact.
For every result URL in your list that meets the stated requirement, you will earn 1 point, and for
every result URL in your list that does not fit the requirement, you will lose 1 point. Your goal is
to maximize the number of points so if you are able to produce more than 1000 pages that’s
even better, but 1000 is a good goal for the allocated time. Also include which month(s) of the
2020 archives you pulled the URLs from.

## Approach
This task essentially boils down to the following major steps:
1. Fetch objects from AWS S3.
2. Filter relevant objects (web pages) based on some criteria (in this case, pages archived from year 2020).
3. Scrape pages for relevant content ("Covid-19" and "Economy") and extract URLs of pages where the content criteria 
   is met.

### Ideas
- We can leverage **AWS CLI** or `boto3` to list and filter relevant archives and fetch items.
- We can use `warcio` package to extract (or de-compress) archived pages.
- We can use regex to identify relevant content.

## Implementation
### Filter and fetch relevant archives
- Using the `boto3` python package, we can interface with AWS and perform queries on S3 buckets.
- In this case we target the archives for year **2020** as shown below:
    ```python
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("commoncrawl")
    
    objects = bucket.objects.filter(Prefix="crawl-data/CC-MAIN-2020")
    ```

### Scrape for keywords using regex
We want pages that contain content relevant to "Covid-19" and its impact on the "economy". A simple way to do this 
is by:
- Scrape only pages of type "response" as only those contain actual content w.r.t the keywords we're looking for.
- Using a regex that checks for the occurrence for the terms "covid-19", "economy" and their corresponding variants 
  in the HTML contents of the extracted archives.

### Steps
1. Configure AWS credentials. This can be done in one of two ways:
   - Use `aws configure` in CLI.
   - Enter credentials when prompted by the `get_warc.py` script.
2. Setup your python environment.
    ```python
    pip install -r requirements.txt
    ```
3. Extract list of relevant `warc.gz` file URIs (in this case for the year 2020). If you have already configured 
   your aws credentials via CLI, enter empty values for prompts.
    ```python
    python get_warc.py
    Please provide your AWS access key:
    Please provide your AWS secret key:
    ```
   The script can take roughly 10-15 mins to fully extract the list of 2020 archives (numbering in ~170,000) and 
   will save the same to a file named `warc_2020_all.txt`.
4. Finally, run the extraction script to scrape the list of archived pages and fetch relevant URLs.
   ```python
   python get_covid_economy_urls
   ```
   The output will be printed to console and written to `covid_economy_urls_2020.txt`.

## Potential Improvements
- Make the scripts more generic and parameterized.
- Use a more sophisticated scraping criteria (for eg, NLP) than just plain regex match. Not all pages with key-word 
  matches 
  necessarily fit the criteria of Covid and its impact on the economy.
- Improve archive URI filteration and fetch performance by optimizing queries on AWS.
- Improve scraping performance via tokenization of HTML and multi-processing.
