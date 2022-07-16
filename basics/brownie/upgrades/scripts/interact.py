from brownie import (
    SimpleStorageV2,
    TransparentUpgradeableProxy,
    SimpleStorage,
    Contract,
)
from scripts.helpers import get_account


def main():
    account = get_account()
    proxy = TransparentUpgradeableProxy[-1]
    proxy_storage = Contract.from_abi("SimpleStorage", proxy.address, SimpleStorage.abi)
    print(f"Starting value: {proxy_storage.retrieve()}")

    proxy_storage.store(10, {"from": account})
    print(f"Value after store: {proxy_storage.retrieve()}")

    proxy_storage = Contract.from_abi(
        "SimpleStorageV2", proxy.address, SimpleStorageV2.abi
    )
    print(f"Starting value on v2: {proxy_storage.retrieve()}")

    proxy_storage.increment({"from": account})
    print(f"Value after increment: {proxy_storage.retrieve()}")

    proxy_storage = Contract.from_abi("SimpleStorage", proxy.address, SimpleStorage.abi)
    print(f"Ending value on v1: {proxy_storage.retrieve()}")
