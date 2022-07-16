from scripts.helpers import get_account, get_price_feed_address, is_not_dev_network
from brownie import FundMe


def deploy_fund_me():
    account = get_account()
    fund_me = FundMe.deploy(
        get_price_feed_address(),
        {"from": account},
        publish_source=is_not_dev_network(),
    )
    print(f"Contract deployed at: {fund_me.address}")
    return fund_me


def main():
    deploy_fund_me()
