from web3 import Web3
from brownie import DappToken
from scripts.helpers import get_account, is_not_dev_network
import pytest


def test_dapp_token_can_be_deployed_with_initial_supply():
    if is_not_dev_network():
        pytest.skip()
    owner = get_account()
    initial_supply = Web3.toWei(10000, "ether")
    dapp_token = DappToken.deploy(initial_supply, {"from": owner})
    assert dapp_token.name() == "DAPP TOKEN"
    assert dapp_token.totalSupply() == initial_supply
    assert dapp_token.balanceOf(owner) == Web3.toWei(10000, "ether")
