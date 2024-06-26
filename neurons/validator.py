# The MIT License (MIT)
# Copyright © 2024 OpenKaito

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import json
import os
import random
import time
import wandb
from datetime import datetime, timezone
from traceback import print_exception

# Bittensor
import bittensor as bt
import openai
import torch
from dotenv import load_dotenv

import openkaito
from openkaito import __version__
from openkaito.base.validator import BaseValidatorNeuron
from openkaito.crawlers.twitter.apidojo import ApiDojoTwitterCrawler
from openkaito.crawlers.twitter.microworlds import MicroworldsTwitterCrawler
from openkaito.evaluation.evaluator import Evaluator
from openkaito.protocol import SearchSynapse
from openkaito.tasks import (
    generate_author_index_task,
    generate_structured_search_task,
    random_query,
)
from openkaito.utils.uids import get_random_uids
from openkaito.utils.version import get_version


class Validator(BaseValidatorNeuron):

    def __init__(self):
        super(Validator, self).__init__()
        load_dotenv()

        # for ranking results evaluation
        llm_client = openai.OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            organization=os.getenv("OPENAI_ORGANIZATION"),
            max_retries=3,
        )

        # for integrity check
        # twitter_crawler = MicroworldsTwitterCrawler(os.environ["APIFY_API_KEY"])
        twitter_crawler = ApiDojoTwitterCrawler(os.environ["APIFY_API_KEY"])

        self.evaluator = Evaluator(llm_client, twitter_crawler)

        with open("twitter_usernames.txt") as f:
            twitter_usernames = f.read().strip().splitlines()
        self.twitter_usernames = twitter_usernames

        if os.getenv("WANDB_API_KEY") is None:
            bt.logging.warning(
                "!!! WANDB_API_KEY not found in environment variables. You are strongly recommended to set it. We may enforce to make it required in the future."
            )
            self.config.neuron.wandb_off = True

        if not self.config.neuron.wandb_off:
            wandb.login(key=os.environ["WANDB_API_KEY"], verify=True, relogin=True)
            wandb.init(
                project=f"sn{self.config.netuid}-validators",
                entity="subnet-openkaito",
                config={
                    "hotkey": self.wallet.hotkey.ss58_address,
                },
                name=f"validator-{self.uid}-{__version__}",
                resume="auto",
                dir=self.config.neuron.full_path,
            )

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        try:
            miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
            random_number = random.random()
            bt.logging.info(f"[CST] random_number: {random_number}")
            # mixed tasks, deprecated SearchSynapse
            if random_number < 0:
                query_string = random_query(input_file="queries.txt")
                search_query = SearchSynapse(
                    query_string=query_string,
                    size=self.config.neuron.search_result_size,
                    version=get_version(),
                )
                search_query.timeout = 90
            else:
                # 80% chance to send index author data task with crawling and indexing
                #if random_number < 0.8:
                if random_number < 0:
                    search_query = generate_author_index_task(
                        size=10,  # author index data size
                        num_authors=2,
                    )
                    # this is a bootstrap task for users to crawl more data from the author list.
                    # miners may implement a more efficient way to crawl and index the author data in the background,
                    # instead of relying on the validator tasks
                    search_query.timeout = 90

                    bt.logging.info(
                        f"[CST] Sending {search_query.name}: author index data task, authors:{search_query.author_usernames} to miner uids: {miner_uids}"
                    )
                # 10% chance to send author search task without crawling
                #elif random_number < 0.9:
                elif random_number < 0:
                    search_query = generate_author_index_task(
                        size=10,  # author index data size
                        num_authors=2,
                    )
                    search_query.timeout = 10

                    bt.logging.info(
                        f"[CST] Sending {search_query.name}: author index data task (timeout = 10), authors:{search_query.author_usernames} to miner uids: {miner_uids}"
                    )
                # 10% chance to send structured search task
                else:
                    search_query = generate_structured_search_task(
                        size=self.config.neuron.search_result_size,
                        author_usernames=random.sample(self.twitter_usernames, 100),
                    )
                    search_query.timeout = 90

                    bt.logging.info(
                        f"[CST] Sending structured_search_task {search_query.name}: {search_query.query_string} to miner uids: {miner_uids}"
                    )
            bt.logging.trace(
                f"[CST] miners: {[(uid, self.metagraph.axons[uid] )for uid in miner_uids]}"
            )

            # The dendrite client queries the network.
            responses = await self.dendrite(
                # Send the query to selected miner axons in the network.
                axons=[self.metagraph.axons[uid] for uid in miner_uids],
                synapse=search_query,
                deserialize=True,
                timeout=search_query.timeout,
            )

            # Log the results for monitoring purposes.
            bt.logging.debug(f"[CST] Received responses: {responses}")

            rewards = self.evaluator.evaluate(search_query, responses)

            bt.logging.info(f"[CST] Scored responses: {rewards} for {miner_uids}")

            self.update_scores(rewards, miner_uids)

            if not self.config.neuron.wandb_off:
                wandb_log = {
                    "synapse": search_query.json(),
                    "scores": {
                        uid.item(): reward.item()
                        for uid, reward in zip(miner_uids, rewards)
                    },
                    "responses": {
                        uid.item(): json.dumps(response)
                        for uid, response in zip(miner_uids, responses)
                    },
                }
                wandb.log(wandb_log)
                bt.logging.debug("wandb_log", wandb_log)
            else:
                bt.logging.warning(
                    "!!! WANDB is not enabled. You are strongly recommended to obtain and set WANDB_API_KEY. We may enforce to make it required in the future."
                )

        except Exception as e:
            bt.logging.error(f"Error during forward: {e}")
            bt.logging.debug(print_exception(type(e), e, e.__traceback__))

    def run(self):
        # Check that validator is registered on the network.
        self.sync()

        bt.logging.info(f"Validator starting at block: {self.block}")

        # This loop maintains the validator's operations until intentionally stopped.
        try:
            while True:
                bt.logging.info(f"step({self.step}) block({self.block})")

                # Run multiple forwards concurrently.
                self.loop.run_until_complete(self.concurrent_forward())

                # Check if we should exit.
                if self.should_exit:
                    break

                # Sync metagraph and potentially set weights.
                self.sync()

                self.step += 1

                # Sleep interval before the next iteration.
                time.sleep(self.config.neuron.search_request_interval)

        # If someone intentionally stops the validator, it'll safely terminate operations.
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Validator killed by keyboard interrupt.")
            exit()

        # In case of unforeseen errors, the validator will log the error and exit. (restart by pm2)
        except Exception as err:
            bt.logging.error("Error during validation", str(err))
            bt.logging.debug(print_exception(type(err), err, err.__traceback__))
            self.should_exit = True

    def print_info(self):
        metagraph = self.metagraph
        self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)

        log = (
            "Validator | "
            f"Step:{self.step} | "
            f"UID:{self.uid} | "
            f"Block:{self.block} | "
            f"Stake:{metagraph.S[self.uid]} | "
            f"VTrust:{metagraph.Tv[self.uid]} | "
            f"Dividend:{metagraph.D[self.uid]} | "
            f"Emission:{metagraph.E[self.uid]}"
        )
        bt.logging.info(log)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            validator.print_info()
            if validator.should_exit:
                bt.logging.warning("Ending validator...")
                break

            time.sleep(30)
