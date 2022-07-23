import json
import yaml
from scripts.helpers import (
    get_account,
    is_not_dev_network,
    eth_to_wei,
    should_update_front_end,
)
from scripts.dependencies import get_contract_address
from brownie import DappToken, TokenFarm

ALLOWED_TOKENS = {"weth_token": "eth_usd_price_feed", "fau_token": "dai_usd_price_feed"}


def deploy_dapp_token():
    return DappToken.deploy(eth_to_wei(10000), {"from": get_account()})


def deploy_token_farm(dapp_token):
    return TokenFarm.deploy(
        dapp_token,
        get_contract_address("dai_usd_price_feed"),
        {"from": get_account()},
        publish_source=is_not_dev_network(),
    )


def transfer_dapp_token_to_farm(dapp_token, token_farm):
    tx = dapp_token.transfer(
        token_farm,
        dapp_token.totalSupply() - eth_to_wei(100),
        {"from": get_account()},
    )
    tx.wait(1)


def allow_a_token(token_farm, token_name):
    token = get_contract_address(token_name)
    price_feed = get_contract_address(ALLOWED_TOKENS[token_name])
    tx = token_farm.addAllowedToken(token, price_feed, {"from": get_account()})
    tx.wait(1)


def add_extra_allowed_tokens_to_farm(token_farm):
    for token_name in ALLOWED_TOKENS:
        allow_a_token(token_farm, token_name)


def update_front_end():
    with open("brownie-config.yaml", "r") as brownie_config_yaml:
        config_dict = yaml.load(brownie_config_yaml, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)


def deploy():
    dapp_token = deploy_dapp_token()
    token_farm = deploy_token_farm(dapp_token)
    transfer_dapp_token_to_farm(dapp_token, token_farm)
    add_extra_allowed_tokens_to_farm(token_farm)
    if should_update_front_end():
        update_front_end()


def main():
    deploy()
