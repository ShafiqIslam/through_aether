from scripts.dependencies import get_mock_contract
from scripts.helpers import is_not_local_network, get_account
from scripts.advanced_collectible.deploy import deploy
from scripts.advanced_collectible.create_token import create_token
import pytest
from brownie import accounts


def create_token_and_fulfill_random(collectible, account, random):
    create_tx = create_token(account)

    get_mock_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        create_tx.events["RequestedCollectible"]["requestId"],
        collectible.address,
        [random],
        {"from": get_account()},
    )


def test_advanced_collectible_create_token():
    if is_not_local_network():
        pytest.skip()

    collectible = deploy()
    create_token_and_fulfill_random(collectible, get_account(), 8)

    assert collectible.getTokenCount() == 1
    assert collectible.getBreedNameOf(0) == "ST_BERNARD"
    assert collectible.ownerOf(0) == get_account()


def test_advanced_collectible_create_multiple_token():
    if is_not_local_network():
        pytest.skip()

    collectible = deploy()
    create_token_and_fulfill_random(collectible, get_account(), 8)
    create_token_and_fulfill_random(collectible, accounts[1], 12)

    assert collectible.getTokenCount() == 2
    assert collectible.getBreedNameOf(1) == "PUG"
    assert collectible.ownerOf(1) == accounts[1]
