from scripts.helpers import get_account, eth_to_wei
from brownie import DappToken, MockWETH, MockFAU


def main():
    print(eth_to_wei(100) / 1e18)

    account = get_account()
    dapp_token = DappToken[-1]
    print(dapp_token.totalSupply() / 1e18)
    print(dapp_token.balanceOf(account) / 1e18)

    weth = MockWETH[-1]
    print(weth.totalSupply() / 1e18)
    print(weth.balanceOf(account) / 1e18)

    fau = MockFAU[-1]
    print(fau.totalSupply() / 1e18)
    print(fau.balanceOf(account) / 1e18)
