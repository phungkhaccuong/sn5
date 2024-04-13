import argparse
import os
import random

import bittensor as bt
import openai
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from openkaito.crawlers.twitter.apidojo import ApiDojoTwitterCrawler
from openkaito.crawlers.twitter.microworlds import MicroworldsTwitterCrawler
from openkaito.evaluation.evaluator import Evaluator
from openkaito.protocol import SearchSynapse, SortType, StructuredSearchSynapse
from openkaito.search.ranking.heuristic_ranking import HeuristicRankingModel
from openkaito.search.structured_search_engine import StructuredSearchEngine
from openkaito.tasks import generate_author_index_task


def main():
    load_dotenv()
    bt.logging.set_debug(True)
    bt.logging.set_trace(True)

    # for ranking results evaluation
    llm_client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORGANIZATION"),
        max_retries=3,
    )

    twitter_crawler = None
    # # for integrity check
    # twitter_crawler = ApiDojoTwitterCrawler(os.environ["APIFY_API_KEY"])
    evaluator = Evaluator(llm_client, twitter_crawler)

    # search_client = Elasticsearch(
    #     os.environ["ELASTICSEARCH_HOST"],
    #     basic_auth=(
    #         os.environ["ELASTICSEARCH_USERNAME"],
    #         os.environ["ELASTICSEARCH_PASSWORD"],
    #     ),
    #     verify_certs=False,
    #     ssl_show_warn=False,
    # )
    #
    # search_engine = StructuredSearchEngine(
    #     search_client=search_client,
    #     relevance_ranking_model=HeuristicRankingModel(
    #         length_weight=0.8, age_weight=0.2
    #     ),
    #     twitter_crawler=None,
    # )

    # search_query = StructuredSearchSynapse(
    #     size=10, author_usernames=["elonmusk", "nftbadger"]
    # )
    # search_query = generate_author_index_task(size=10, num_authors=100)
    # print(search_query)

    # docs = search_engine.search(search_query=search_query)
    # print("======documents======")
    # print(docs)

    docs =  [{'id': '1756031921585541257', 'text': '“There’s no great secret in fortune making. All you have to do is buy cheap and sell, act with thrift and shrewdness and then be persistent.”\xa0- by Hetty Green aka the Witch of Wall Street', 'created_at': '2024-02-09T19:06:50+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1756031921585541257', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 3}, {'id': '1745203795712467003', 'text': 'Historical day for #Bitcoin  . Bitcoin remains beautiful and elegant, just as it was designed from day 1. A new era begins and we are ready for the next battle 🔥🙏', 'created_at': '2024-01-10T21:59:43+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1745203795712467003', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 3}, {'id': '1741872576358707663', 'text': 'Gonna be a wild 2024 full of events 🔥. Crypto + AI + Energy innovation ready to take off 🐉 (🙏@fredwilson)', 'created_at': '2024-01-01T17:22:39+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1741872576358707663', 'quote_count': 0, 'reply_count': 1, 'retweet_count': 0, 'favorite_count': 3}, {'id': '1741894212323619253', 'text': '@fredwilson These are still playing out nicely under the 3 megatrends that won\'t stop anytime soon: (1) The Great Debasement of Currency; (2) The golden era of the "creator" economy; (3) Maximizing access to cheap energy for everyone 🚀', 'created_at': '2024-01-01T18:48:37+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1741894212323619253', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 1}, {'id': '1749868650453193159', 'text': 'Unbundling the Game Engine: The Rise of Next Generation 3D Creation Engines https://t.co/LpUYHxsErQ', 'created_at': '2024-01-23T18:56:11+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1749868650453193159', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 1}, {'id': '1742425015881252944', 'text': '2024, the year of Azuki ⛩️ https://t.co/RYSBl5LfMl', 'created_at': '2024-01-03T05:57:51+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1742425015881252944', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 4}, {'id': '1745886720946831494', 'text': 'Happy 2nd anniversary, Azuki ⛩️', 'created_at': '2024-01-12T19:13:25+00:00', 'username': 'jindo139', 'url': 'https://x.com/jindo139/status/1745886720946831494', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 3}, {'id': '1771209204642070789', 'text': 'my body is ready', 'created_at': '2024-03-22T16:15:56+00:00', 'username': 'friendtechnique', 'url': 'https://x.com/friendtechnique/status/1771209204642070789', 'quote_count': 0, 'reply_count': 0, 'retweet_count': 0, 'favorite_count': 2}, {'id': '1726800135815127131', 'text': "It's time to BLAST OFF\n\n@BLAST_L2 is the L2 with native yield backed by @Paradigm and @StandardCrypto\n\nJoin Blast Early Access to start earning yield + Blast Points, redeemable in May", 'created_at': '2023-11-21T03:10:09+00:00', 'username': 'friendtechnique', 'url': 'https://x.com/friendtechnique/status/1726800135815127131', 'quote_count': 0, 'reply_count': 1, 'retweet_count': 0, 'favorite_count': 0}, {'id': '1710431757361697140', 'text': 'RT @hunktech_eth: Fairly new, but great stats. Happy to bond with @friendtechnique .\n\nKeep up the good behaviour fren. Honor to bond with y…', 'created_at': '2023-10-06T23:08:03+00:00', 'username': 'friendtechnique', 'url': 'https://x.com/friendtechnique/status/1710431757361697140', 'quote_count': 0, 'reply_count': 1, 'retweet_count': 1, 'favorite_count': 4}]

    score = evaluator.llm_author_index_data_evaluation(docs)
    print("======LLM Score======")
    print(score)


if __name__ == "__main__":
    main()
