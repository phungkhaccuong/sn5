import argparse
import os
import random

import bittensor as bt
import openai
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from openkaito.crawlers.twitter.microworlds import MicroworldsTwitterCrawler
from openkaito.evaluation.evaluator import Evaluator
from openkaito.protocol import SearchSynapse, SortType, StructuredSearchSynapse
from openkaito.search.ranking.heuristic_ranking import HeuristicRankingModel
from openkaito.search.structured_search_engine import StructuredSearchEngine


def parse_args():
    parser = argparse.ArgumentParser(description="Miner Search Ranking Evaluation")
    parser.add_argument("--query", type=str, default="BTC", help="query string")
    parser.add_argument(
        "--size", type=int, default=10, help="size of the response items"
    )
    # parser.add_argument('--crawling', type=bool, default=False, action='store_true', help='crawling data before search')

    return parser.parse_args()


def main():
    args = parse_args()
    print(vars(args))
    load_dotenv()
    bt.logging.set_trace(True)

    # for ranking results evaluation
    llm_client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORGANIZATION"),
        max_retries=3,
    )

    # # for integrity check
    # twitter_crawler = ApifyTwitterCrawler(os.environ["APIFY_API_KEY"])
    evaluator = Evaluator(llm_client, None)

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

    search_engine = StructuredSearchEngine(
        search_client=search_client,
        relevance_ranking_model=ranking_model,
        twitter_crawler=None,
    )

    search_query = StructuredSearchSynapse(
        author_usernames=['HsakaTrades'],
        size=10,
    )

    print(search_query)

    ranked_docs = search_engine.search(search_query=search_query)
    print("======ranked documents  ======")
    print(ranked_docs)

    ranked_docs = [{'id': '1774213419471720547', 'text': 'RT @HsakaTrades: "wolf is this the fated last cycle?"\n\nidk, I doubt it\n\nthough if you do trade it as such, trying to extract every ounce of…', 'created_at': '2024-03-30T23:13:37+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1774213419471720547', 'quote_count': 13, 'reply_count': 104, 'retweet_count': 120, 'favorite_count': 2483, 'choice': 'somewhat insightful', 'reason': 'The text discusses trading cycles and extracting value, offering partial insights into trading strategies.'},
                   {'id': '1774040239721381969', 'text': 'RT @HsakaTrades: gm fellow unsophisticated market participants \n\nmemecoins volume dominance will simply continue rising until \n\nsome meme b…', 'created_at': '2024-03-30T11:45:27+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1774040239721381969', 'quote_count': 26, 'reply_count': 171, 'retweet_count': 161, 'favorite_count': 2107, 'choice': 'somewhat insightful', 'reason': 'The text mentions memecoins dominance, offering partial insights into market trends.'},
                   {'id': '1773788004974292995', 'text': 'put on the hat a month ago\n\nwhen most people had already printed and were talking about shorting the nance listings\n\nabout to hit a 10x with 0 mins spent underwater\n\n\U0001fae1 https://t.co/X3GnS9xk3b', 'created_at': '2024-03-29T19:03:10+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1773788004974292995', 'quote_count': 19, 'reply_count': 127, 'retweet_count': 201, 'favorite_count': 2159, 'choice': 'somewhat insightful', 'reason': 'The text talks about successful trading strategies, offering partial insights into market behavior.'},
                   {'id': '1773196174020767993', 'text': 'Blackrock US$ Flow: 323.8 million\n\nimagine thinking he would let fidelity outnumber him https://t.co/Tbqi7LPGdZ', 'created_at': '2024-03-28T03:51:26+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1773196174020767993', 'quote_count': 7, 'reply_count': 76, 'retweet_count': 113, 'favorite_count': 1307, 'choice': 'somewhat insightful', 'reason': "The text discusses Blackrock's US$ flow, offering partial insights into financial movements."},
                   {'id': '1773149248944492874', 'text': 'Investors retreat back into safe havens after recent Coinbase lawsuit news jolts the market https://t.co/FoklAkKivk', 'created_at': '2024-03-28T00:44:59+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1773149248944492874', 'quote_count': 34, 'reply_count': 214, 'retweet_count': 334, 'favorite_count': 2701, 'choice': 'somewhat insightful', 'reason': 'The text mentions investors retreating to safe havens after market news, providing partial insights into market reactions.'},
                   {'id': '1773140859980050809', 'text': 'okay, elon is on his philanthropy arc\n\nsame happened to a bunch of other accs (bloomberg joe, g,)\n\nSchopenhauer was right, free will is an illusion.\n\nwill start tweeting airdrop threads soon https://t.co/mWI3KEgFH1', 'created_at': '2024-03-28T00:11:39+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1773140859980050809', 'quote_count': 0, 'reply_count': 35, 'retweet_count': 7, 'favorite_count': 358, 'choice': 'somewhat insightful', 'reason': 'The text mentions changes in account behaviors, offering partial insights into social media dynamics.'},
                   {'id': '1773132827934015597', 'text': "can't determine if this is what's happening\n\nnot seeing any signs of unauthorized access so far\n\nbut can't be sure\n\ndon't click on links etc from this acc for the time being", 'created_at': '2024-03-27T23:39:44+00:00', 'username': 'HsakaTrades', 'url': 'https://x.com/HsakaTrades/status/1773132827934015597', 'quote_count': 1, 'reply_count': 74, 'retweet_count': 5, 'favorite_count': 457, 'choice': 'somewhat insightful', 'reason': 'The text talks about potential security issues, offering partial insights into cybersecurity.'},
                   {'id': '1774045741532553354',
                    'text': 'the VCs whinging about the explosion of interest in memecoins are directly responsible for it\n\nwith their incessant predatory tokenomics low float high fdv shenanigans \n\nthey bit the hand that fed them, now the same hand has dropped them off at the shelter, and taken in a more friendly dog',
                    'created_at': '2024-03-30T12:07:19+00:00', 'username': 'HsakaTrades',
                    'url': 'https://x.com/HsakaTrades/status/1774045741532553354', 'quote_count': 74,
                    'reply_count': 224, 'retweet_count': 419, 'favorite_count': 2496, 'choice': 'insightful',
                    'reason': "The text provides insights into the dynamics of memecoins and VCs' roles in their popularity."},
                   {'id': '1774014990304895093',
                    'text': "CT avoid making statements about permanent changes in market dynamics based on a few months of activity challenge [impossible]\n\nThis one's on top, then that one's on top, and on and on, the wheel simply continues spinning. https://t.co/zKeTYeKz5E",
                    'created_at': '2024-03-30T10:05:07+00:00', 'username': 'HsakaTrades',
                    'url': 'https://x.com/HsakaTrades/status/1774014990304895093', 'quote_count': 2, 'reply_count': 74,
                    'retweet_count': 62, 'favorite_count': 928, 'choice': 'insightful',
                    'reason': 'The text challenges making permanent market dynamics based on short-term activities, providing insightful commentary.'},
                   {'id': '1778112572153028802',
                    'text': 'I, for one, am grateful for the sophisticated market participants that keep hedging their locked tokens\n\n&gt;lets us long the best performing coins without paying exorbitant funding rates\n&gt;keep fueling the rallies as their hedge is blown up https://t.co/nWI4Rhqoar',
                    'created_at': '2024-04-10T17:27:27+00:00', 'username': 'HsakaTrades',
                    'url': 'https://x.com/HsakaTrades/status/1778112572153028802', 'quote_count': 15, 'reply_count': 81,
                    'retweet_count': 76, 'favorite_count': 1103, 'choice': 'somewhat insightful',
                    'reason': 'The text mentions sophisticated market participants hedging locked tokens, providing some insight into market dynamics.'},

                   ]

    # note this is the llm score, skipped integrity check and batch age score
    score = evaluator.llm_author_index_data_evaluation(ranked_docs)
    print("======LLM Score   ======")
    print(score)


if __name__ == "__main__":
    main()
