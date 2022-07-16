from brownie import (
    SimpleStorageV2,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    Contract,
)
from scripts.helpers import get_account, upgrade_via_proxy, is_not_dev_network


def upgrade():
    account = get_account()
    simple_storage_v2 = SimpleStorageV2.deploy(
        {"from": account},
        publish_source=is_not_dev_network(),
    )
    proxy = TransparentUpgradeableProxy[-1]
    upgrade_via_proxy(account, proxy, simple_storage_v2, ProxyAdmin[-1])

    return Contract.from_abi("SimpleStorageV2", proxy.address, SimpleStorageV2.abi)


def main():
    upgrade()
