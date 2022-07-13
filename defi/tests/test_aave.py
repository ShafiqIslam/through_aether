from scripts.helpers import get_weth_token
from scripts.aave import (
    get_dai_vs_eth_price,
    get_lending_pool,
    approve_erc20,
    get_account,
)


def test_get_asset_price():
    asset_price = get_dai_vs_eth_price()

    assert asset_price > 0


def test_get_lending_pool():
    lending_pool = get_lending_pool()

    assert lending_pool != None


def test_approve_erc20():
    account = get_account()
    lending_pool = get_lending_pool()
    amount = 1000000000000000000  # 1
    erc20_address = get_weth_token()

    approved = approve_erc20(amount, lending_pool.address, erc20_address, account)

    assert approved is True
