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


def encode_function_data(initializer=None, *args):
    if not len(args):
        args = b""

    if initializer:
        return initializer.encode_input(*args)

    return b""


def upgrade_via_proxy(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction
