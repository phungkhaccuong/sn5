import os

import bittensor as bt
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from openkaito.crawlers.twitter.apidojo import ApiDojoTwitterCrawler
from openkaito.protocol import StructuredSearchSynapse
from openkaito.search.ranking import HeuristicRankingModel
from openkaito.search.structured_search_engine import StructuredSearchEngine
from openkaito.utils.version import get_version


def main():
    load_dotenv()
    bt.logging.set_debug(True)

    crawl_size = 50

    twitter_crawler = ApiDojoTwitterCrawler(os.environ["APIFY_API_KEY"])
    search_client = Elasticsearch(
        os.environ["ELASTICSEARCH_HOST"],
        basic_auth=(
            os.environ["ELASTICSEARCH_USERNAME"],
            os.environ["ELASTICSEARCH_PASSWORD"],
        ),
        verify_certs=False,
        ssl_show_warn=False,
    )
    search_engine = StructuredSearchEngine(
        search_client=search_client,
        relevance_ranking_model=HeuristicRankingModel(
            length_weight=0.4, age_weight=0.6
        ),
        twitter_crawler=twitter_crawler,
    )

    with open("twitter_usernames.txt") as f:
        twitter_usernames = f.read().strip().splitlines()

    for i in range(0, 10):
        bt.logging.info(f"Index:{i} - user_name:{twitter_usernames[i]}")
        query = StructuredSearchSynapse(
            size=crawl_size,
            author_usernames=[twitter_usernames[i]],
            version=get_version(),
        )

        search_engine.crawl_and_index_data(
            query_string=query.query_string,
            author_usernames=query.author_usernames,
            max_size=query.size,
        )


if __name__ == "__main__":
    main()