from web3 import Web3
from brownie import (
    DappToken,
    TokenFarm,
    MockWETH,
    MockFAU,
    MockV3AggregatorETHUSD,
    MockV3AggregatorDAIUSD,
    accounts,
    exceptions,
)
import pytest

unit_test = pytest.mark.require_network("development")


@pytest.fixture
def owner():
    return accounts[0]


@pytest.fixture
def user_1():
    return accounts[1]


@pytest.fixture
def user_2():
    return accounts[2]


@pytest.fixture
def tokens_and_feeds(owner):
    return (
        MockWETH.deploy({"from": owner}),
        MockV3AggregatorETHUSD.deploy(8, 2000 * 10**8, {"from": owner}),
        MockFAU.deploy({"from": owner}),
        MockV3AggregatorDAIUSD.deploy(8, 1 * 10**8, {"from": owner}),
    )


@pytest.fixture
def dapp_token(owner, user_1, user_2):
    token = DappToken.deploy(Web3.toWei(10000, "ether"), {"from": owner})
    token.transfer(user_1, Web3.toWei(2, "ether"), {"from": owner})
    token.transfer(user_2, Web3.toWei(2, "ether"), {"from": owner})
    return token


@pytest.fixture
def token_farm(dapp_token, owner, tokens_and_feeds):
    (_, _, _, fau_token_feed) = tokens_and_feeds
    return TokenFarm.deploy(dapp_token, fau_token_feed, {"from": owner})


@pytest.fixture
def allowed_token_farm(token_farm, owner, tokens_and_feeds):
    (weth_token, weth_price_feed, fau_token, fau_price_feed) = tokens_and_feeds
    token_farm.addAllowedToken(weth_token, weth_price_feed, {"from": owner}).wait(1)
    token_farm.addAllowedToken(fau_token, fau_price_feed, {"from": owner}).wait(1)
    return token_farm


@unit_test
def test_token_farm_is_deployed_with_ownership(token_farm, owner):
    assert token_farm.owner() == owner


@unit_test
def test_token_farm_is_deployed_with_dapp_token(dapp_token, token_farm):
    assert token_farm.isTokenAllowed(dapp_token) == True
    assert token_farm.getTokenValueWRTWei(dapp_token) == Web3.toWei(1, "ether")


@unit_test
def test_tokens_can_be_allowed_with_price_feed(token_farm, owner, tokens_and_feeds):
    (weth_token, weth_price_feed, fau_token, fau_price_feed) = tokens_and_feeds

    token_farm.addAllowedToken(weth_token, weth_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(weth_token) == True
    assert token_farm.getTokenValueWRTWei(weth_token) == Web3.toWei(2000, "ether")
    assert token_farm.isTokenAllowed(fau_token) == False

    token_farm.addAllowedToken(fau_token, fau_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(fau_token) == True
    assert token_farm.getTokenValueWRTWei(fau_token) == Web3.toWei(1, "ether")
    assert token_farm.isTokenAllowed(weth_token) == True
    assert token_farm.getTokenValueWRTWei(weth_token) == Web3.toWei(2000, "ether")


@unit_test
def test_only_owner_can_allow_token(token_farm, owner, user_1, tokens_and_feeds):
    (token, price_feed, _, _) = tokens_and_feeds

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedToken(token, price_feed, {"from": user_1})

    assert token_farm.isTokenAllowed(token) == False

    token_farm.addAllowedToken(token, price_feed, {"from": owner}).wait(1)
    assert token_farm.isTokenAllowed(token) == True


@unit_test
def test_zero_token_cant_be_staked(token_farm, dapp_token, owner):
    amount_staked = 0
    dapp_token.approve(token_farm, amount_staked, {"from": owner})

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stake(dapp_token, amount_staked, {"from": owner})


@unit_test
def test_unallowed_token_cant_be_staked(token_farm, tokens_and_feeds, owner):
    (weth_token, _, _, _) = tokens_and_feeds
    amount_staked = Web3.toWei(1, "ether")
    weth_token.approve(token_farm, amount_staked, {"from": owner})

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stake(weth_token, amount_staked, {"from": owner})


@unit_test
def test_stake_makes_user_stakeholder(allowed_token_farm, dapp_token, owner, user_1):
    assert allowed_token_farm.isStakeholder(owner) == False

    amount_staked = Web3.toWei(1, "ether")
    dapp_token.approve(allowed_token_farm, amount_staked, {"from": owner})
    allowed_token_farm.stake(dapp_token, amount_staked, {"from": owner})

    assert allowed_token_farm.isStakeholder(owner) == True
    assert allowed_token_farm.isStakeholder(user_1) == False

    dapp_token.approve(allowed_token_farm, amount_staked, {"from": user_1})
    allowed_token_farm.stake(dapp_token, amount_staked, {"from": user_1})

    assert allowed_token_farm.isStakeholder(user_1) == True
    assert allowed_token_farm.isStakeholder(owner) == True


@unit_test
def test_stake_makes_user_stakeholder(allowed_token_farm, dapp_token, owner, user_1):
    assert allowed_token_farm.isStakeholder(owner) == False

    amount_staked = Web3.toWei(1, "ether")
    dapp_token.approve(allowed_token_farm, amount_staked, {"from": owner})
    allowed_token_farm.stake(dapp_token, amount_staked, {"from": owner})

    assert allowed_token_farm.isStakeholder(owner) == True
    assert allowed_token_farm.isStakeholder(user_1) == False

    dapp_token.approve(allowed_token_farm, amount_staked, {"from": user_1})
    allowed_token_farm.stake(dapp_token, amount_staked, {"from": user_1})

    assert allowed_token_farm.isStakeholder(user_1) == True
    assert allowed_token_farm.isStakeholder(owner) == True
