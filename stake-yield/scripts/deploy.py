from scripts.helpers import get_account, is_not_dev_network, get_address
from brownie import DappToken, TokenFarm
from web3 import Web3


def deploy_dapp_token():
    return DappToken.deploy({"from": get_account()})


def deploy_token_farm(dapp_token):
    return TokenFarm.deploy(
        dapp_token.address,
        {"from": get_account()},
        publish_source=is_not_dev_network(),
    )


def transfer_dapp_token_to_farm(dapp_token, token_farm):
    tx = dapp_token.transfer(
        token_farm.address,
        dapp_token.totalSupply() - Web3.toWei(100, "ether"),
        {"from": get_account()},
    )
    tx.wait(1)


def allow_a_token(token_farm, token, price_feed):
    add_tx = token_farm.addAllowedTokens(
        token.address, price_feed, {"from": get_account()}
    )
    add_tx.wait(1)


def add_allowed_tokens_to_farm(dapp_token, token_farm):
    weth_token = get_address("weth_token")
    fau_token = get_address("fau_token")
    allowed_tokens = {
        dapp_token: get_address("dai_usd_price_feed"),
        fau_token: get_address("dai_usd_price_feed"),
        weth_token: get_address("eth_usd_price_feed"),
    }

    for token in allowed_tokens:
        allow_a_token(token_farm, token, allowed_tokens[token])


def deploy():
    dapp_token = deploy_dapp_token()
    token_farm = deploy_token_farm(dapp_token)
    transfer_dapp_token_to_farm(dapp_token, token_farm)
    add_allowed_tokens_to_farm(dapp_token, token_farm)


def main():
    deploy()
