from scripts.helpers import get_account, is_not_dev_network
from scripts.deploy import deploy_fund_me
from brownie import accounts, exceptions
import pytest


def test_can_fund():
    account = get_account()
    fund_me = deploy_fund_me()
    amount = fund_me.getEntranceFee()
    fund_me.fund({"from": account, "value": amount})
    assert fund_me.funded(account.address) == amount


def test_can_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    amount = fund_me.getEntranceFee()
    fund_me.fund({"from": account, "value": amount})
    fund_me.withdraw({"from": account})
    assert fund_me.funded(account.address) == 0


def test_only_owner_can_withdraw():
    if is_not_dev_network():
        pytest.skip("only for local testing")

    fund_me = deploy_fund_me()
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": accounts[1]})
