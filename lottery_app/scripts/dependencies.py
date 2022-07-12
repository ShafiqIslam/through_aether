from web3 import Web3
from scripts.helpers import (
    is_not_local_network,
    get_active_network_config,
    get_dev_account,
    is_dev_network,
    get_vrf_subscription_id,
)
from brownie import MockV3Aggregator, VRFCoordinatorV2Mock


def deploy_vrf_coordinator():
    base_fee = 100000
    gas_price_link = 100000
    vrf_mock = VRFCoordinatorV2Mock.deploy(
        base_fee,
        gas_price_link,
        {"from": get_dev_account()},
    )

    subscriptionTx = vrf_mock.createSubscription()
    subId = subscriptionTx.events["SubscriptionCreated"]["subId"]
    vrf_mock.fundSubscription(subId, Web3.toWei("1", "ether"))


def deploy_v3_aggegator():
    decimals = 8
    starting_price = 2000
    starting_price_wrt_gwei = starting_price * (10**decimals)
    MockV3Aggregator.deploy(
        decimals,
        starting_price_wrt_gwei,
        {"from": get_dev_account()},
    )


DEPENDENCY_MOCKS = {
    "eth_usd_price_feed": {
        "type": MockV3Aggregator,
        "function": deploy_v3_aggegator,
    },
    "vrf_coordinator": {
        "type": VRFCoordinatorV2Mock,
        "function": deploy_vrf_coordinator,
    },
}


def get_mock_contract(name):
    mock = DEPENDENCY_MOCKS[name]
    if len(mock["type"]) == 0:
        mock["function"]()
    return mock["type"][-1]


def get_address(dependency):
    if is_not_local_network():
        return get_active_network_config()[dependency]

    return get_mock_contract(dependency).address


def get_price_feed_address():
    return get_address("eth_usd_price_feed")


def get_vrf_coordinator_address():
    return get_address("vrf_coordinator")


def add_lottery_contract_to_vrf_subscription(lottery):
    if is_dev_network():
        get_mock_contract("vrf_coordinator").addConsumer(
            get_vrf_subscription_id(), lottery.address
        )
