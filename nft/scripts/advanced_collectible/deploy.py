from brownie import AdvancedCollectible
from scripts.dependencies import (
    get_vrf_coordinator_address,
    add_contract_to_vrf_subscription,
    get_vrf_subscription_id,
)
from scripts.helpers import (
    get_account,
    get_vrf_key_hash,
    is_not_dev_network,
)


def deploy():
    account = get_account()
    advanced_collectible = AdvancedCollectible.deploy(
        get_vrf_coordinator_address(),
        get_vrf_key_hash(),
        get_vrf_subscription_id(),
        {"from": account},
        publish_source=is_not_dev_network(),
    )
    add_contract_to_vrf_subscription(advanced_collectible)
    return advanced_collectible


def main():
    deploy()
