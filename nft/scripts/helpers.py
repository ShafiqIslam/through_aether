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


def get_vrf_key_hash():
    return get_active_network_config()["vrf_key_hash"]


def get_open_sea_url(contract, token_id):
    opensea_url = "https://testnets.opensea.io/assets/{}/{}"
    return opensea_url.format(contract.address, token_id)
