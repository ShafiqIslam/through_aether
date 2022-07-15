from brownie import AdvancedCollectible
from scripts.helpers import get_account


def create_token(account):
    advanced_collectible = AdvancedCollectible[-1]
    create_tx = advanced_collectible.create({"from": account})
    create_tx.wait(1)
    return create_tx


def main():
    create_token(get_account())
