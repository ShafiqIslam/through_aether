from brownie import MyToken
from scripts.helpers import get_account
from web3 import Web3


def main():
    our_token = MyToken.deploy(Web3.toWei(1000, "ether"), {"from": get_account()})
    print(our_token.name())
