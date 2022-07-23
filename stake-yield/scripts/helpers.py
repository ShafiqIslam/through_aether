from brownie import network, accounts, config
from web3 import Web3


LOCAL_BLOCKCHAINS = ["development", "ganache-local"]
FORKED_BLOCKCHAINS = ["mainnet-fork"]


def get_account():
    if is_using_dummy_accounts():
        return get_dev_account()
    else:
        return accounts.add(config["wallets"]["owner"])


def is_using_dummy_accounts():
    return is_dev_network() and network.show_active() != "ganache-local"


def is_dev_network():
    return (
        network.show_active() in LOCAL_BLOCKCHAINS
        or network.show_active() in FORKED_BLOCKCHAINS
    )


def is_not_dev_network():
    return not is_dev_network()


def is_local_network():
    return network.show_active() in LOCAL_BLOCKCHAINS


def is_not_local_network():
    return not is_local_network()


def is_unit_test_network():
    return network.show_active() == "development"


def should_update_front_end():
    return not is_unit_test_network()


def get_dev_account():
    return accounts[0]


def get_active_network_config():
    return config["networks"][network.show_active()]


def eth_to_wei(eth):
    return Web3.toWei(eth, "ether")
