from brownie import network, accounts, config

LOCAL_BLOCKCHAINS = ["development", "ganache-local"]
FORKED_BLOCKCHAINS = ["mainnet-fork"]


def get_account():
    if is_dev_network():
        return get_dev_account()
    else:
        return accounts.add(config["wallets"]["owner"])


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


def get_dev_account():
    return accounts[0]


def get_active_network_config():
    return config["networks"][network.show_active()]


def get_weth_token():
    return get_active_network_config()["weth_token"]


def get_dai_token():
    return get_active_network_config()["dai_token"]


def get_lending_pool_addresses_provider_token():
    return get_active_network_config()["lpap_token"]


def get_dai_eth_price_feed_address():
    return get_active_network_config()["dai_eth_price_feed"]
