from scripts.helpers import (
    is_not_local_network,
    get_active_network_config,
    get_dev_account,
    is_local_network,
)
from brownie import MockV3AggregatorDAIUSD, MockV3AggregatorETHUSD, MockWETH, MockFAU, Contract


def deploy_v3_aggegator(contract_type, decimals, starting_price):
    starting_price_wrt_gwei = starting_price * (10**decimals)
    contract_type.deploy(
        decimals,
        starting_price_wrt_gwei,
        {"from": get_dev_account()},
    )

def deploy_mock_token(contract_type):
    contract_type.deploy({"from": get_dev_account()})


DEPENDENCY_MOCKS = {
    "eth_usd_price_feed": {
        "type": MockV3AggregatorETHUSD,
        "function": deploy_v3_aggegator,
        "args": [MockV3AggregatorETHUSD, 8, 2000],
    },
    "dai_usd_price_feed": {
        "type": MockV3AggregatorDAIUSD,
        "function": deploy_v3_aggegator,
        "args": [MockV3AggregatorDAIUSD, 8, 1],
    },
    "weth_token": {
        "type": MockWETH,
        "function": deploy_mock_token,
        "args": [MockWETH],
    },
    "fau_token": {
        "type": MockFAU,
        "function": deploy_mock_token,
        "args": [MockFAU],
    },
}


def get_mock_contract(name):
    mock = DEPENDENCY_MOCKS[name]
    if len(mock["type"]) == 0:
        mock["function"](*mock["args"])
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


def get_contract_address(dependency):
    if is_not_local_network():
        return get_dependency_address_from_active_netwrok(dependency)

    return get_mock_contract(dependency).address
