from web3 import Web3
from scripts.helpers import (
    is_dev_network,
    get_lending_pool_addresses_provider_token,
    get_account,
    get_weth_token,
    get_dai_eth_price_feed_address,
    get_dai_token,
)
from scripts.get_weth import get_weth
from brownie import interface


def main():
    if is_dev_network():
        get_weth()

    amount = Web3.toWei(0.05, "ether")
    lending_pool = get_lending_pool()

    deposit(lending_pool, amount)
    borrowable_eth, _ = get_account_stat(lending_pool)

    borrow(lending_pool, get_eth_to_dai(borrowable_eth * 0.95))
    get_account_stat(lending_pool)

    repay(lending_pool, amount)
    get_account_stat(lending_pool)


def get_lending_pool():
    address_provider = interface.ILendingPoolAddressesProvider(
        get_lending_pool_addresses_provider_token()
    )
    lending_pool_address = address_provider.getLendingPool()
    return interface.ILendingPool(lending_pool_address)


def approve_deposit_of_weth(sender, amount):
    return approve_erc20(get_weth_token(), sender, amount, "depositing WETH")


def approve_erc20(erc20_token, sender, amount, _for):
    print(f"Approving ERC20 ({_for}) ...")
    erc20 = interface.IERC20(erc20_token)
    tx = erc20.approve(sender, amount, {"from": get_account()})
    tx.wait(1)
    print(f"Approved ERC20 ({_for}).\n\n")
    return tx


def deposit(lending_pool, amount):
    approve_deposit_of_weth(lending_pool.address, amount)

    eth_amount = Web3.fromWei(amount, "ether")
    print(f"Depositing {eth_amount} WETH ...")
    account = get_account()
    tx = lending_pool.deposit(
        get_weth_token(), amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited.\n\n")
    return tx


def borrow(lending_pool, amount):
    print(f"Borrowing {amount} DAI ...")
    amount = Web3.toWei(amount, "ether")
    account = get_account()
    tx = lending_pool.borrow(
        get_dai_token(), amount, 1, 0, account.address, {"from": account}
    )
    tx.wait(1)
    print("Borrowed.\n\n")
    return tx


def repay(lending_pool, amount):
    approve_repay_of_dai(lending_pool.address, amount)

    eth_amount = Web3.fromWei(amount, "ether")
    print(f"Repaying {eth_amount} ETH ...")

    account = get_account()
    tx = lending_pool.repay(
        get_dai_token(), amount, 1, account.address, {"from": account}
    )
    tx.wait(1)
    print("Repaid.\n\n")
    return tx


def approve_repay_of_dai(sender, amount):
    return approve_erc20(get_dai_token(), sender, amount, "repaying DAI")


def get_eth_to_dai(eth):
    return eth / get_dai_vs_eth_price()


def get_dai_vs_eth_price():
    price_feed = interface.IAggregatorV3(get_dai_eth_price_feed_address())
    price = price_feed.latestRoundData()[1]
    price = float(Web3.fromWei(price, "ether"))
    print(f"DAI/ETH price = {price}\n\n")
    return price


def get_account_stat(lending_pool):
    account = get_account()
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        tlv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print("User account stat")
    print("-----------------")
    print(f"ETH deposited  : {total_collateral_eth}")
    print(f"ETH borrowed   : {total_debt_eth}")
    print(f"ETH borrowable : {available_borrow_eth}\n\n")
    return (float(available_borrow_eth), float(total_debt_eth))
