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


def __deploy_token(token, owner, user_1, user_2):
    token = token.deploy(Web3.toWei(10000, "ether"), {"from": owner})
    token.transfer(user_1, Web3.toWei(100, "ether"), {"from": owner})
    token.transfer(user_2, Web3.toWei(100, "ether"), {"from": owner})
    return token


@pytest.fixture
def tokens_and_feeds(owner, user_1, user_2):
    return (
        __deploy_token(MockWETH, owner, user_1, user_2),
        MockV3AggregatorETHUSD.deploy(8, 2000 * 10**8, {"from": owner}),
        __deploy_token(MockFAU, owner, user_1, user_2),
        MockV3AggregatorDAIUSD.deploy(8, 1 * 10**8, {"from": owner}),
    )


@pytest.fixture
def dapp_token(owner, user_1, user_2):
    return __deploy_token(DappToken, owner, user_1, user_2)


@pytest.fixture
def token_farm(dapp_token, owner, tokens_and_feeds):
    (_, _, _, fau_token_feed) = tokens_and_feeds
    return TokenFarm.deploy(dapp_token, fau_token_feed, {"from": owner})


@pytest.fixture
def allowed_token_farm(token_farm, owner, tokens_and_feeds):
    (weth_token, weth_price_feed, fau_token, fau_price_feed) = tokens_and_feeds
    token_farm.addAllowedToken(weth_token, weth_price_feed, {"from": owner}).wait(1)
    token_farm.addAllowedToken(fau_token, fau_price_feed, {"from": owner}).wait(1)
    return (token_farm, weth_token, fau_token)


@unit_test
def test_token_farm_is_deployed_with_ownership(token_farm, owner):
    assert token_farm.owner() == owner


@unit_test
def test_token_farm_is_deployed_with_dapp_token(dapp_token, token_farm):
    assert token_farm.isTokenAllowed(dapp_token) == True
    assert token_farm.getTokenUnitValue(dapp_token) == Web3.toWei(1, "ether")


@unit_test
def test_tokens_can_be_allowed_with_price_feed(token_farm, owner, tokens_and_feeds):
    (weth_token, weth_price_feed, fau_token, fau_price_feed) = tokens_and_feeds

    token_farm.addAllowedToken(weth_token, weth_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(weth_token) == True
    assert token_farm.getTokenUnitValue(weth_token) == Web3.toWei(2000, "ether")
    assert token_farm.isTokenAllowed(fau_token) == False

    token_farm.addAllowedToken(fau_token, fau_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(fau_token) == True
    assert token_farm.getTokenUnitValue(fau_token) == Web3.toWei(1, "ether")
    assert token_farm.isTokenAllowed(weth_token) == True
    assert token_farm.getTokenUnitValue(weth_token) == Web3.toWei(2000, "ether")


@unit_test
def test_only_owner_can_allow_token(token_farm, owner, user_1, tokens_and_feeds):
    (token, price_feed, _, _) = tokens_and_feeds

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedToken(token, price_feed, {"from": user_1})

    assert token_farm.isTokenAllowed(token) == False

    token_farm.addAllowedToken(token, price_feed, {"from": owner}).wait(1)
    assert token_farm.isTokenAllowed(token) == True


def __stake(token_farm, token, user, ether):
    amount = 0 if ether == 0 else Web3.toWei(ether, "ether")
    token.approve(token_farm, amount, {"from": user})
    token_farm.stake(token, amount, {"from": user})


@unit_test
def test_zero_token_cant_be_staked(token_farm, dapp_token, owner):
    with pytest.raises(exceptions.VirtualMachineError):
        __stake(token_farm, dapp_token, owner, 0)


@unit_test
def test_unallowed_token_cant_be_staked(token_farm, tokens_and_feeds, owner):
    (weth_token, _, _, _) = tokens_and_feeds
    with pytest.raises(exceptions.VirtualMachineError):
        __stake(token_farm, weth_token, owner, 1)


@unit_test
def test_stake_transfers_token_from_user_to_farm(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    assert weth.balanceOf(token_farm) == 0
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(user_1) == 100 * 1e18
    assert fau.balanceOf(user_1) == 100 * 1e18
    assert weth.balanceOf(user_2) == 100 * 1e18
    assert fau.balanceOf(user_2) == 100 * 1e18

    __stake(token_farm, weth, user_1, 1)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(user_1) == 99 * 1e18
    assert fau.balanceOf(user_1) == 100 * 1e18
    assert weth.balanceOf(user_2) == 100 * 1e18
    assert fau.balanceOf(user_2) == 100 * 1e18

    __stake(token_farm, fau, user_2, 2)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 2 * 1e18
    assert weth.balanceOf(user_1) == 99 * 1e18
    assert fau.balanceOf(user_1) == 100 * 1e18
    assert weth.balanceOf(user_2) == 100 * 1e18
    assert fau.balanceOf(user_2) == 98 * 1e18

    __stake(token_farm, fau, user_1, 5)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(user_1) == 99 * 1e18
    assert fau.balanceOf(user_1) == 95 * 1e18
    assert weth.balanceOf(user_2) == 100 * 1e18
    assert fau.balanceOf(user_2) == 98 * 1e18

    __stake(token_farm, weth, user_2, 10)
    assert weth.balanceOf(token_farm) == 11 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(user_1) == 99 * 1e18
    assert fau.balanceOf(user_1) == 95 * 1e18
    assert weth.balanceOf(user_2) == 90 * 1e18
    assert fau.balanceOf(user_2) == 98 * 1e18


@unit_test
def test_stake_makes_user_stakeholder(allowed_token_farm, dapp_token, owner, user_1):
    (token_farm, _, _) = allowed_token_farm

    assert token_farm.isStakeholder(owner) == False
    assert token_farm.isStakeholder(user_1) == False

    __stake(token_farm, dapp_token, owner, 1)
    assert token_farm.isStakeholder(owner) == True
    assert token_farm.isStakeholder(user_1) == False

    __stake(token_farm, dapp_token, user_1, 1)
    assert token_farm.isStakeholder(user_1) == True
    assert token_farm.isStakeholder(owner) == True


@unit_test
def test_stake_increases_total_token_balance(allowed_token_farm, owner, user_1):
    (token_farm, weth, fau) = allowed_token_farm

    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, weth, owner, 1)
    assert token_farm.getTotalStakedToken(weth) == 1e18
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, weth, user_1, 2)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, fau, owner, 5)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 5e18

    __stake(token_farm, fau, user_1, 6)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 11e18


@unit_test
def test_stake_increases_stakeholder_token_balance(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_1, fau)
        token_farm.getStakeholderTokenBalance(user_1, weth)
        token_farm.getStakeholderTokenBalance(user_2, weth)
        token_farm.getStakeholderTokenBalance(user_2, fau)

    __stake(token_farm, weth, user_1, 1)
    assert token_farm.getStakeholderTokenBalance(user_1, weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(user_1, fau) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_2, weth)
        token_farm.getStakeholderTokenBalance(user_2, fau)

    __stake(token_farm, fau, user_1, 2)
    assert token_farm.getStakeholderTokenBalance(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(user_1, weth) == 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_2, weth)
        token_farm.getStakeholderTokenBalance(user_2, fau)

    __stake(token_farm, weth, user_2, 5)
    assert token_farm.getStakeholderTokenBalance(user_1, weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(user_2, weth) == 5e18
    assert token_farm.getStakeholderTokenBalance(user_2, fau) == 0

    __stake(token_farm, fau, user_2, 6)
    assert token_farm.getStakeholderTokenBalance(user_1, weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(user_2, weth) == 5e18
    assert token_farm.getStakeholderTokenBalance(user_2, fau) == 6e18


@unit_test
def test_stake_increases_stakeholder_token_value(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_1, weth)
        token_farm.getStakeholderTokenValue(user_1, fau)
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, weth, user_1, 1)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, fau, user_1, 2)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, weth, user_2, 5)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenValue(user_2, weth) == 1e22
    assert token_farm.getStakeholderTokenValue(user_2, fau) == 0

    __stake(token_farm, fau, user_2, 6)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenValue(user_2, weth) == 1e22
    assert token_farm.getStakeholderTokenValue(user_2, fau) == 6e18


@unit_test
def test_stake_increases_stakeholder_total_value(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_1)
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, weth, user_1, 1)
    assert token_farm.getStakeholderTotalValue(user_1) == 2000 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, fau, user_1, 2)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, weth, user_2, 5)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(user_2) == 10000 * 1e18

    __stake(token_farm, fau, user_2, 6)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(user_2) == 10006 * 1e18


@pytest.fixture
def staked_token_farm(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    __stake(token_farm, weth, user_1, 1)
    __stake(token_farm, fau, user_1, 5)
    __stake(token_farm, weth, user_2, 10)
    __stake(token_farm, fau, user_2, 2)

    return (token_farm, weth, fau)


@unit_test
def test_non_stakeholder_cant_unstake(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.unstake(weth, {"from": user_1})
        token_farm.unstake(fau, {"from": user_2})


@unit_test
def test_cant_unstake_unstaked_token(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm
    __stake(token_farm, weth, user_1, 1)
    __stake(token_farm, fau, user_2, 1)

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.unstake(fau, {"from": user_1})
        token_farm.unstake(weth, {"from": user_2})


@unit_test
def test_unstake_transfers_token_from_farm_to_user(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    __stake(token_farm, weth, user_1, 1)
    __stake(token_farm, fau, user_1, 5)
    __stake(token_farm, weth, user_2, 10)
    __stake(token_farm, fau, user_2, 2)

    token_farm.unstake(weth, {"from": user_1})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(user_1) == 100 * 1e18
    assert fau.balanceOf(user_1) == 95 * 1e18
    assert weth.balanceOf(user_2) == 90 * 1e18
    assert fau.balanceOf(user_2) == 98 * 1e18

    token_farm.unstake(fau, {"from": user_2})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 5 * 1e18
    assert weth.balanceOf(user_1) == 100 * 1e18
    assert fau.balanceOf(user_1) == 95 * 1e18
    assert weth.balanceOf(user_2) == 90 * 1e18
    assert fau.balanceOf(user_2) == 100 * 1e18

    token_farm.unstake(fau, {"from": user_1})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(user_1) == 100 * 1e18
    assert fau.balanceOf(user_1) == 100 * 1e18
    assert weth.balanceOf(user_2) == 90 * 1e18
    assert fau.balanceOf(user_2) == 100 * 1e18

    token_farm.unstake(weth, {"from": user_2})
    assert weth.balanceOf(token_farm) == 0
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(user_1) == 100 * 1e18
    assert fau.balanceOf(user_1) == 100 * 1e18
    assert weth.balanceOf(user_2) == 100 * 1e18
    assert fau.balanceOf(user_2) == 100 * 1e18


@unit_test
def test_unstake_decreases_total_token_balance(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    __stake(token_farm, weth, user_1, 1)
    __stake(token_farm, fau, user_1, 5)
    __stake(token_farm, weth, user_2, 10)
    __stake(token_farm, fau, user_2, 2)

    token_farm.unstake(weth, {"from": user_1})
    assert token_farm.getTotalStakedToken(weth) == 10 * 1e18
    assert token_farm.getTotalStakedToken(fau) == 7 * 1e18

    token_farm.unstake(fau, {"from": user_2})
    assert token_farm.getTotalStakedToken(weth) == 10 * 1e18
    assert token_farm.getTotalStakedToken(fau) == 5 * 1e18

    token_farm.unstake(weth, {"from": user_2})
    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 5 * 1e18

    token_farm.unstake(fau, {"from": user_1})
    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 0


@unit_test
def test_unstake_decreases_stakeholder_token_balance(
    allowed_token_farm, user_1, user_2
):
    (token_farm, weth, fau) = allowed_token_farm

    __stake(token_farm, weth, user_1, 1)
    __stake(token_farm, fau, user_1, 5)
    __stake(token_farm, weth, user_2, 10)
    __stake(token_farm, fau, user_2, 2)

    token_farm.unstake(weth, {"from": user_1})
    assert token_farm.getStakeholderTokenBalance(user_1, weth) == 0
    assert token_farm.getStakeholderTokenBalance(user_1, fau) == 5 * 1e18
    assert token_farm.getStakeholderTokenBalance(user_2, weth) == 10 * 1e18
    assert token_farm.getStakeholderTokenBalance(user_2, fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": user_1})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_1, weth)
        token_farm.getStakeholderTokenBalance(user_1, fau)
    assert token_farm.getStakeholderTokenBalance(user_2, weth) == 10 * 1e18
    assert token_farm.getStakeholderTokenBalance(user_2, fau) == 2 * 1e18

    token_farm.unstake(weth, {"from": user_2})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_1, weth)
        token_farm.getStakeholderTokenBalance(user_1, fau)
    assert token_farm.getStakeholderTokenBalance(user_2, weth) == 0
    assert token_farm.getStakeholderTokenBalance(user_2, fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": user_2})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(user_1, weth)
        token_farm.getStakeholderTokenBalance(user_1, fau)
        token_farm.getStakeholderTokenBalance(user_2, weth)
        token_farm.getStakeholderTokenBalance(user_2, fau)


@unit_test
def test_stake_increases_stakeholder_token_value(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_1, weth)
        token_farm.getStakeholderTokenValue(user_1, fau)
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, weth, user_1, 1)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, fau, user_1, 2)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(user_2, weth)
        token_farm.getStakeholderTokenValue(user_2, fau)

    __stake(token_farm, weth, user_2, 5)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenValue(user_2, weth) == 1e22
    assert token_farm.getStakeholderTokenValue(user_2, fau) == 0

    __stake(token_farm, fau, user_2, 6)
    assert token_farm.getStakeholderTokenValue(user_1, weth) == 2e21
    assert token_farm.getStakeholderTokenValue(user_1, fau) == 2e18
    assert token_farm.getStakeholderTokenValue(user_2, weth) == 1e22
    assert token_farm.getStakeholderTokenValue(user_2, fau) == 6e18


@unit_test
def test_stake_increases_stakeholder_total_value(allowed_token_farm, user_1, user_2):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_1)
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, weth, user_1, 1)
    assert token_farm.getStakeholderTotalValue(user_1) == 2000 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, fau, user_1, 2)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(user_2)

    __stake(token_farm, weth, user_2, 5)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(user_2) == 10000 * 1e18

    __stake(token_farm, fau, user_2, 6)
    assert token_farm.getStakeholderTotalValue(user_1) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(user_2) == 10006 * 1e18


@unit_test
def test_stake_makes_user_stakeholder(allowed_token_farm, dapp_token, owner, user_1):
    (token_farm, _, _) = allowed_token_farm

    assert token_farm.isStakeholder(owner) == False
    assert token_farm.isStakeholder(user_1) == False

    __stake(token_farm, dapp_token, owner, 1)
    assert token_farm.isStakeholder(owner) == True
    assert token_farm.isStakeholder(user_1) == False

    __stake(token_farm, dapp_token, user_1, 1)
    assert token_farm.isStakeholder(user_1) == True
    assert token_farm.isStakeholder(owner) == True
