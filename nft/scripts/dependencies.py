from web3 import Web3
from scripts.helpers import (
    is_not_local_network,
    get_active_network_config,
    get_dev_account,
    get_account,
    is_dev_network,
    is_local_network,
)
from brownie import VRFCoordinatorV2Mock, Contract

MOCK_SUBSCRIPTION_ID = 1


def deploy_vrf_coordinator():
    base_fee = 100000
    gas_price_link = 100000
    vrf_mock = VRFCoordinatorV2Mock.deploy(
        base_fee,
        gas_price_link,
        {"from": get_dev_account()},
    )

    subscriptionTx = vrf_mock.createSubscription()
    MOCK_SUBSCRIPTION_ID = subscriptionTx.events["SubscriptionCreated"]["subId"]
    vrf_mock.fundSubscription(MOCK_SUBSCRIPTION_ID, Web3.toWei("1", "ether"))


DEPENDENCY_MOCKS = {
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


def get_real_contract(name):
    # mock and real both have same name and abi
    contract_type = DEPENDENCY_MOCKS[name]["type"]
    contract_address = get_dependency_address_from_active_netwrok(name)
    return Contract.from_abi(contract_type._name, contract_address, contract_type.abi)


def get_contract(name):
    return get_mock_contract(name) if is_local_network() else get_real_contract(name)


def get_dependency_address_from_active_netwrok(dependency):
    return get_active_network_config()[dependency]


def get_address(dependency):
    if is_not_local_network():
        return get_dependency_address_from_active_netwrok(dependency)

    return get_mock_contract(dependency).address


def get_vrf_coordinator_address():
    return get_address("vrf_coordinator")


def add_contract_to_vrf_subscription(vrf_consumer):
    vrf_coordinator = get_contract("vrf_coordinator")
    subscription_id = get_vrf_subscription_id()
    subscription_details = vrf_coordinator.getSubscription(subscription_id)
    if vrf_consumer in subscription_details[3]:
        return

    account = get_account()
    tx = vrf_coordinator.addConsumer(
        subscription_id, vrf_consumer.address, {"from": account}
    )
    tx.wait(1)
    return tx


def get_vrf_subscription_id():
    if is_dev_network():
        return MOCK_SUBSCRIPTION_ID
    return get_active_network_config()["vrf_subscription_id"]
