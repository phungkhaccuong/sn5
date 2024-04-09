import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from openkaito.crawlers.twitter.apidojo import ApiDojoTwitterCrawler
from openkaito.search.ranking import HeuristicRankingModel
from openkaito.search.structured_search_engine import StructuredSearchEngine


class CrawlJob():
    NUMBER_USERNAMES = 100;

    def __init__(self):
        self.twitter_usernames = None
        load_dotenv()

        search_client = Elasticsearch(
            os.environ["ELASTICSEARCH_HOST"],
            basic_auth=(
                os.environ["ELASTICSEARCH_USERNAME"],
                os.environ["ELASTICSEARCH_PASSWORD"],
            ),
            verify_certs=False,
            ssl_show_warn=False,
        )

        # for ranking recalled results
        ranking_model = HeuristicRankingModel(length_weight=0.8, age_weight=0.2)

        # optional, for crawling data
        twitter_crawler = (
            ApiDojoTwitterCrawler(os.environ["APIFY_API_KEY"])
            if os.environ.get("APIFY_API_KEY")
            else None
        )

        self.structured_search_engine = StructuredSearchEngine(
            search_client=search_client,
            relevance_ranking_model=ranking_model,
            twitter_crawler=twitter_crawler
        )

    def crawl(self, author_usernames: list = None, crawl_size: int = 100):
        if len(author_usernames) > 0:
            self.structured_search_engine.crawl_and_index_data(
                None,
                author_usernames=author_usernames,
                max_size=crawl_size,
            )

    def load_authors(self):
        with open("./../twitter_usernames.txt") as f:
            twitter_usernames = f.read().strip().splitlines()
        self.twitter_usernames = twitter_usernames

    def run(self):
        self.load_authors()
        print("load usernames successful")
        for i in range(0, len(self.twitter_usernames), CrawlJob.NUMBER_USERNAMES):
            print(f"I:{i}")
            usernames = self.twitter_usernames[:CrawlJob.NUMBER_USERNAMES]
            self.crawl(usernames, 200)
            self.twitter_usernames = self.twitter_usernames[CrawlJob.NUMBER_USERNAMES:]
            break;


if __name__ == "__main__":
    print("Start job...")
    job = CrawlJob()
    while True:
        job.run()
        time.sleep(60*60)
