from brownie import accounts, config, SimpleStorage


def deploy_simple_storage():
    account = accounts.add(config["wallets"]["from_key"])
    simple_storage = SimpleStorage.deploy({"from": account})
    print(simple_storage.retrieve())
    simple_storage.store(10, {"from": account}).wait(1)
    print(simple_storage.retrieve())


def main():
    deploy_simple_storage()
