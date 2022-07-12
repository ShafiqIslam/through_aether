from brownie import network, accounts, config

LOCAL_BLOCKCHAINS = ["development", "ganache-local"]
FORKED_BLOCKCHAINS = ["mainnet-fork"]


def get_account():
    if is_dev_network():
        return get_dev_account()
    else:
        return accounts.add(config["wallets"]["owner_private_key"])


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


def get_network_default_config():
    return config["networks"]["defaults"]


def get_network_config():
    return (
        get_network_default_config()
        if is_dev_network()
        else get_active_network_config()
    )


def get_vrf_key_hash():
    return get_network_config()["vrf_key_hash"]


def get_vrf_subscription_id():
    return get_network_config()["vrf_subscription_id"]
