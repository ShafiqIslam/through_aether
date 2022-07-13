from web3 import Web3
from scripts.helpers import get_account, get_weth_token
from brownie import interface


def get_weth():
    print("Requesting WETH...")
    account = get_account()
    weth = interface.IWeth(get_weth_token())
    tx = weth.deposit({"from": account, "value": Web3.toWei(0.05, "ether")})
    tx.wait(1)
    print("Received 0.05 WETH.\n\n")
    return tx


def main():
    get_weth()
