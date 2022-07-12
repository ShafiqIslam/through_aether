from scripts.dependencies import (
    get_price_feed_address,
    get_vrf_coordinator_address,
    add_lottery_contract_to_vrf_subscription,
)
from scripts.helpers import (
    get_account,
    get_vrf_key_hash,
    get_vrf_subscription_id,
    is_not_dev_network,
)
from brownie import Lottery


def deploy():
    account = get_account()
    lottery = Lottery.deploy(
        get_price_feed_address(),
        get_vrf_coordinator_address(),
        get_vrf_key_hash(),
        get_vrf_subscription_id(),
        {"from": account},
        publish_source=is_not_dev_network(),
    )
    add_lottery_contract_to_vrf_subscription(lottery)
    return lottery


def main():
    deploy()
