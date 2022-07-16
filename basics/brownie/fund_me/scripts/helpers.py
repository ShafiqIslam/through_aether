from brownie import MockV3Aggregator, network, accounts, config
from web3 import Web3


DECIMALS = 8
STARTING_PRICE = 2000
STARTING_PRICE_WRT_GWEI = STARTING_PRICE * (10**10)
LOCAL_BLOCKCHAINS = ["development", "ganache-local"]


def get_account():
    if is_dev_network():
        return get_dev_account()
    else:
        return accounts.add(config["wallets"]["from_key"])


def is_dev_network():
    return network.show_active() in LOCAL_BLOCKCHAINS


def is_not_dev_network():
    return not is_dev_network()


def get_dev_account():
    return accounts[0]


def get_price_feed_address():
    if is_not_dev_network():
        return config["networks"][network.show_active()]["eth_usd_price_feed"]

    if len(MockV3Aggregator) == 0:
        MockV3Aggregator.deploy(
            DECIMALS,
            STARTING_PRICE_WRT_GWEI,
            {"from": get_dev_account()},
        )
    return MockV3Aggregator[-1].address
