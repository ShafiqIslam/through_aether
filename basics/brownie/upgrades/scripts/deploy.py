from brownie import (
    SimpleStorage,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    Contract,
)
from scripts.helpers import get_account, encode_function_data, is_not_dev_network


def deploy():
    account = get_account()
    simple_storage = SimpleStorage.deploy(
        {"from": account},
        publish_source=is_not_dev_network(),
    )

    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
    )

    proxy = TransparentUpgradeableProxy.deploy(
        simple_storage.address,
        proxy_admin.address,
        encode_function_data(),
        {"from": account, "gas_limit": 1000000},
    )

    return Contract.from_abi("SimpleStorage", proxy.address, SimpleStorage.abi)


def main():
    deploy()
