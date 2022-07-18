from scripts.helpers import (
    is_not_local_network,
    get_active_network_config,
    get_dev_account,
    is_local_network,
)
from brownie import MockV3Aggregator, Contract


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
