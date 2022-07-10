from brownie import accounts, SimpleStorage


def test_deploy():
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})
    assert simple_storage.retrieve() == 0


def test_update_storage():
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})
    simple_storage.store(10, {"from": account})
    assert simple_storage.retrieve() == 10
