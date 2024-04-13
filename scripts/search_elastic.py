import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from openkaito.crawlers.twitter.apidojo import ApiDojoTwitterCrawler
from openkaito.search.ranking import HeuristicRankingModel
from openkaito.search.structured_search_engine import StructuredSearchEngine
import bittensor as bt


class SearchElasticSearch():
    def __init__(self):
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

    def run(self, search_query):
        ranked_docs = self.structured_search_engine.search(search_query=search_query)
        print("======ranked documents======")
        print(ranked_docs)

if __name__ == "__main__":
    query = {'query': {'bool': {'must': [{'terms': {'username': ['SmartBiZon']}}]}}, 'size': 50}
    search = SearchElasticSearch()
    search.run(query)


