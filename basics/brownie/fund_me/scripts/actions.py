from brownie import FundMe
from scripts.helpers import get_account


def fund():
    fund_me = FundMe[-1]
    entrance_fee = fund_me.getEntranceFee()
    print(f"Entrance fee is: {entrance_fee}")
    fund_me.fund({"from": get_account(), "value": entrance_fee})


def withdraw():
    fund_me = FundMe[-1]
    fund_me.withdraw({"from": get_account()})
