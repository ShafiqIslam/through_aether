from brownie import (
    SimpleStorageV2,
    TransparentUpgradeableProxy,
    SimpleStorage,
    Contract,
)
from scripts.deploy import deploy
from scripts.upgrade import upgrade
from scripts.helpers import get_dev_account
import pytest


def test_upgrades():
    deploy()
    upgrade()

    account = get_dev_account()
    proxy = TransparentUpgradeableProxy[-1]
    proxy_storage = Contract.from_abi("SimpleStorage", proxy.address, SimpleStorage.abi)
    assert proxy_storage.retrieve() == 0

    proxy_storage.store(10, {"from": account})
    assert proxy_storage.retrieve() == 10

    proxy_storage = Contract.from_abi(
        "SimpleStorageV2", proxy.address, SimpleStorageV2.abi
    )
    assert proxy_storage.retrieve() == 10

    proxy_storage.increment({"from": account})
    assert proxy_storage.retrieve() == 11

    proxy_storage = Contract.from_abi("SimpleStorage", proxy.address, SimpleStorage.abi)
    assert proxy_storage.retrieve() == 11

    with pytest.raises(AttributeError):
        proxy_storage.increment({"from": account})
