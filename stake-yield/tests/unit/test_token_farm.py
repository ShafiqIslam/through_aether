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


def __deploy_token(token, owner, users):
    token = token.deploy(Web3.toWei(10000, "ether"), {"from": owner})
    token.transfer(users[0], Web3.toWei(100, "ether"), {"from": owner})
    token.transfer(users[1], Web3.toWei(100, "ether"), {"from": owner})
    return token


def __stake(token_farm, token, user, ether):
    amount = 0 if ether == 0 else Web3.toWei(ether, "ether")
    token.approve(token_farm, amount, {"from": user})
    token_farm.stake(token, amount, {"from": user})


@pytest.fixture
def owner():
    return accounts[0]


@pytest.fixture
def users():
    return [accounts[1], accounts[2]]


@pytest.fixture
def tokens_and_feeds(owner, users):
    return (
        __deploy_token(MockWETH, owner, users),
        MockV3AggregatorETHUSD.deploy(8, 2000 * 10**8, {"from": owner}),
        __deploy_token(MockFAU, owner, users),
        MockV3AggregatorDAIUSD.deploy(8, 1 * 10**8, {"from": owner}),
    )


@pytest.fixture
def dapp_token(owner, users):
    return __deploy_token(DappToken, owner, users)


@pytest.fixture
def token_farm(dapp_token, owner, tokens_and_feeds):
    (_, _, _, fau_feed) = tokens_and_feeds
    token_farm = TokenFarm.deploy(dapp_token, fau_feed, {"from": owner})
    dapp_token.approve(token_farm, Web3.toWei(10000, "ether"), {"from": owner})
    return token_farm


@pytest.fixture
def allowed_token_farm(token_farm, owner, tokens_and_feeds):
    (weth, weth_price_feed, fau, fau_price_feed) = tokens_and_feeds
    token_farm.addAllowedToken(weth, weth_price_feed, {"from": owner}).wait(1)
    token_farm.addAllowedToken(fau, fau_price_feed, {"from": owner}).wait(1)
    return (token_farm, weth, fau)


@pytest.fixture
def staked_token_farm(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm

    __stake(token_farm, weth, users[0], 1)
    __stake(token_farm, fau, users[0], 5)
    __stake(token_farm, weth, users[1], 10)
    __stake(token_farm, fau, users[1], 2)

    return (token_farm, weth, fau)


@unit_test
def test_token_farm_is_deployed_with_ownership(token_farm, owner):
    assert token_farm.owner() == owner


@unit_test
def test_token_farm_is_deployed_with_dapp_token(dapp_token, token_farm):
    assert token_farm.isTokenAllowed(dapp_token) == True
    assert token_farm.getTokenUnitValue(dapp_token) == Web3.toWei(1, "ether")


@unit_test
def test_tokens_can_be_allowed_with_price_feed(token_farm, owner, tokens_and_feeds):
    (weth, weth_price_feed, fau, fau_price_feed) = tokens_and_feeds

    token_farm.addAllowedToken(weth, weth_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(weth) == True
    assert token_farm.getTokenUnitValue(weth) == Web3.toWei(2000, "ether")
    assert token_farm.isTokenAllowed(fau) == False

    token_farm.addAllowedToken(fau, fau_price_feed, {"from": owner}).wait(1)

    assert token_farm.isTokenAllowed(fau) == True
    assert token_farm.getTokenUnitValue(fau) == Web3.toWei(1, "ether")
    assert token_farm.isTokenAllowed(weth) == True
    assert token_farm.getTokenUnitValue(weth) == Web3.toWei(2000, "ether")


@unit_test
def test_only_owner_can_allow_token(token_farm, owner, users, tokens_and_feeds):
    (token, price_feed, _, _) = tokens_and_feeds

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedToken(token, price_feed, {"from": users[0]})

    assert token_farm.isTokenAllowed(token) == False

    token_farm.addAllowedToken(token, price_feed, {"from": owner}).wait(1)
    assert token_farm.isTokenAllowed(token) == True


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
def test_stake_transfers_token_from_user_to_farm(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm

    assert weth.balanceOf(token_farm) == 0
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(users[0]) == 100 * 1e18
    assert fau.balanceOf(users[0]) == 100 * 1e18
    assert weth.balanceOf(users[1]) == 100 * 1e18
    assert fau.balanceOf(users[1]) == 100 * 1e18

    __stake(token_farm, weth, users[0], 1)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(users[0]) == 99 * 1e18
    assert fau.balanceOf(users[0]) == 100 * 1e18
    assert weth.balanceOf(users[1]) == 100 * 1e18
    assert fau.balanceOf(users[1]) == 100 * 1e18

    __stake(token_farm, fau, users[1], 2)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 2 * 1e18
    assert weth.balanceOf(users[0]) == 99 * 1e18
    assert fau.balanceOf(users[0]) == 100 * 1e18
    assert weth.balanceOf(users[1]) == 100 * 1e18
    assert fau.balanceOf(users[1]) == 98 * 1e18

    __stake(token_farm, fau, users[0], 5)
    assert weth.balanceOf(token_farm) == 1 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(users[0]) == 99 * 1e18
    assert fau.balanceOf(users[0]) == 95 * 1e18
    assert weth.balanceOf(users[1]) == 100 * 1e18
    assert fau.balanceOf(users[1]) == 98 * 1e18

    __stake(token_farm, weth, users[1], 10)
    assert weth.balanceOf(token_farm) == 11 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(users[0]) == 99 * 1e18
    assert fau.balanceOf(users[0]) == 95 * 1e18
    assert weth.balanceOf(users[1]) == 90 * 1e18
    assert fau.balanceOf(users[1]) == 98 * 1e18


@unit_test
def test_stake_makes_user_stakeholder(allowed_token_farm, dapp_token, owner, users):
    (token_farm, _, _) = allowed_token_farm

    assert token_farm.isStakeholder(owner) == False
    assert token_farm.isStakeholder(users[0]) == False

    __stake(token_farm, dapp_token, owner, 1)
    assert token_farm.isStakeholder(owner) == True
    assert token_farm.isStakeholder(users[0]) == False

    __stake(token_farm, dapp_token, users[0], 1)
    assert token_farm.isStakeholder(users[0]) == True
    assert token_farm.isStakeholder(owner) == True


@unit_test
def test_stake_increases_total_token_balance(allowed_token_farm, owner, users):
    (token_farm, weth, fau) = allowed_token_farm

    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, weth, owner, 1)
    assert token_farm.getTotalStakedToken(weth) == 1e18
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, weth, users[0], 2)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 0

    __stake(token_farm, fau, owner, 5)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 5e18

    __stake(token_farm, fau, users[0], 6)
    assert token_farm.getTotalStakedToken(weth) == 3e18
    assert token_farm.getTotalStakedToken(fau) == 11e18


@unit_test
def test_stake_increases_stakeholder_token_balance(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[0], fau)
        token_farm.getStakeholderTokenBalance(users[0], weth)
        token_farm.getStakeholderTokenBalance(users[1], weth)
        token_farm.getStakeholderTokenBalance(users[1], fau)

    __stake(token_farm, weth, users[0], 1)
    assert token_farm.getStakeholderTokenBalance(users[0], weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(users[0], fau) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[1], weth)
        token_farm.getStakeholderTokenBalance(users[1], fau)

    __stake(token_farm, fau, users[0], 2)
    assert token_farm.getStakeholderTokenBalance(users[0], fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(users[0], weth) == 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[1], weth)
        token_farm.getStakeholderTokenBalance(users[1], fau)

    __stake(token_farm, weth, users[1], 5)
    assert token_farm.getStakeholderTokenBalance(users[0], weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(users[0], fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(users[1], weth) == 5e18
    assert token_farm.getStakeholderTokenBalance(users[1], fau) == 0

    __stake(token_farm, fau, users[1], 6)
    assert token_farm.getStakeholderTokenBalance(users[0], weth) == 1e18
    assert token_farm.getStakeholderTokenBalance(users[0], fau) == 2e18
    assert token_farm.getStakeholderTokenBalance(users[1], weth) == 5e18
    assert token_farm.getStakeholderTokenBalance(users[1], fau) == 6e18


@unit_test
def test_stake_increases_stakeholder_token_value(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[0], weth)
        token_farm.getStakeholderTokenValue(users[0], fau)
        token_farm.getStakeholderTokenValue(users[1], weth)
        token_farm.getStakeholderTokenValue(users[1], fau)

    __stake(token_farm, weth, users[0], 1)
    assert token_farm.getStakeholderTokenValue(users[0], weth) == 2e21
    assert token_farm.getStakeholderTokenValue(users[0], fau) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[1], weth)
        token_farm.getStakeholderTokenValue(users[1], fau)

    __stake(token_farm, fau, users[0], 2)
    assert token_farm.getStakeholderTokenValue(users[0], weth) == 2e21
    assert token_farm.getStakeholderTokenValue(users[0], fau) == 2e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[1], weth)
        token_farm.getStakeholderTokenValue(users[1], fau)

    __stake(token_farm, weth, users[1], 5)
    assert token_farm.getStakeholderTokenValue(users[0], weth) == 2e21
    assert token_farm.getStakeholderTokenValue(users[0], fau) == 2e18
    assert token_farm.getStakeholderTokenValue(users[1], weth) == 1e22
    assert token_farm.getStakeholderTokenValue(users[1], fau) == 0

    __stake(token_farm, fau, users[1], 6)
    assert token_farm.getStakeholderTokenValue(users[0], weth) == 2e21
    assert token_farm.getStakeholderTokenValue(users[0], fau) == 2e18
    assert token_farm.getStakeholderTokenValue(users[1], weth) == 1e22
    assert token_farm.getStakeholderTokenValue(users[1], fau) == 6e18


@unit_test
def test_stake_increases_stakeholder_total_value(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[0])
        token_farm.getStakeholderTotalValue(users[1])

    __stake(token_farm, weth, users[0], 1)
    assert token_farm.getStakeholderTotalValue(users[0]) == 2000 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[1])

    __stake(token_farm, fau, users[0], 2)
    assert token_farm.getStakeholderTotalValue(users[0]) == 2002 * 1e18
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[1])

    __stake(token_farm, weth, users[1], 5)
    assert token_farm.getStakeholderTotalValue(users[0]) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(users[1]) == 10000 * 1e18

    __stake(token_farm, fau, users[1], 6)
    assert token_farm.getStakeholderTotalValue(users[0]) == 2002 * 1e18
    assert token_farm.getStakeholderTotalValue(users[1]) == 10006 * 1e18


@unit_test
def test_non_stakeholder_cant_unstake(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.unstake(weth, {"from": users[0]})
        token_farm.unstake(fau, {"from": users[1]})


@unit_test
def test_cant_unstake_unstaked_token(allowed_token_farm, users):
    (token_farm, weth, fau) = allowed_token_farm
    __stake(token_farm, weth, users[0], 1)
    __stake(token_farm, fau, users[1], 1)

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.unstake(fau, {"from": users[0]})
        token_farm.unstake(weth, {"from": users[1]})


@unit_test
def test_unstake_transfers_token_from_farm_to_user(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 7 * 1e18
    assert weth.balanceOf(users[0]) == 100 * 1e18
    assert fau.balanceOf(users[0]) == 95 * 1e18
    assert weth.balanceOf(users[1]) == 90 * 1e18
    assert fau.balanceOf(users[1]) == 98 * 1e18

    token_farm.unstake(fau, {"from": users[1]})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 5 * 1e18
    assert weth.balanceOf(users[0]) == 100 * 1e18
    assert fau.balanceOf(users[0]) == 95 * 1e18
    assert weth.balanceOf(users[1]) == 90 * 1e18
    assert fau.balanceOf(users[1]) == 100 * 1e18

    token_farm.unstake(fau, {"from": users[0]})
    assert weth.balanceOf(token_farm) == 10 * 1e18
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(users[0]) == 100 * 1e18
    assert fau.balanceOf(users[0]) == 100 * 1e18
    assert weth.balanceOf(users[1]) == 90 * 1e18
    assert fau.balanceOf(users[1]) == 100 * 1e18

    token_farm.unstake(weth, {"from": users[1]})
    assert weth.balanceOf(token_farm) == 0
    assert fau.balanceOf(token_farm) == 0
    assert weth.balanceOf(users[0]) == 100 * 1e18
    assert fau.balanceOf(users[0]) == 100 * 1e18
    assert weth.balanceOf(users[1]) == 100 * 1e18
    assert fau.balanceOf(users[1]) == 100 * 1e18


@unit_test
def test_unstake_decreases_total_token_balance(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert token_farm.getTotalStakedToken(weth) == 10 * 1e18
    assert token_farm.getTotalStakedToken(fau) == 7 * 1e18

    token_farm.unstake(fau, {"from": users[1]})
    assert token_farm.getTotalStakedToken(weth) == 10 * 1e18
    assert token_farm.getTotalStakedToken(fau) == 5 * 1e18

    token_farm.unstake(weth, {"from": users[1]})
    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 5 * 1e18

    token_farm.unstake(fau, {"from": users[0]})
    assert token_farm.getTotalStakedToken(weth) == 0
    assert token_farm.getTotalStakedToken(fau) == 0


@unit_test
def test_unstake_decreases_stakeholder_token_balance(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert token_farm.getStakeholderTokenBalance(users[0], weth) == 0
    assert token_farm.getStakeholderTokenBalance(users[0], fau) == 5 * 1e18
    assert token_farm.getStakeholderTokenBalance(users[1], weth) == 10 * 1e18
    assert token_farm.getStakeholderTokenBalance(users[1], fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": users[0]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[0], weth)
        token_farm.getStakeholderTokenBalance(users[0], fau)
    assert token_farm.getStakeholderTokenBalance(users[1], weth) == 10 * 1e18
    assert token_farm.getStakeholderTokenBalance(users[1], fau) == 2 * 1e18

    token_farm.unstake(weth, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[0], weth)
        token_farm.getStakeholderTokenBalance(users[0], fau)
    assert token_farm.getStakeholderTokenBalance(users[1], weth) == 0
    assert token_farm.getStakeholderTokenBalance(users[1], fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenBalance(users[0], weth)
        token_farm.getStakeholderTokenBalance(users[0], fau)
        token_farm.getStakeholderTokenBalance(users[1], weth)
        token_farm.getStakeholderTokenBalance(users[1], fau)


@unit_test
def test_unstake_decreases_stakeholder_token_value(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert token_farm.getStakeholderTokenValue(users[0], weth) == 0
    assert token_farm.getStakeholderTokenValue(users[0], fau) == 5 * 1e18
    assert token_farm.getStakeholderTokenValue(users[1], weth) == 10 * 2000 * 1e18
    assert token_farm.getStakeholderTokenValue(users[1], fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": users[0]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[0], weth)
        token_farm.getStakeholderTokenValue(users[0], fau)
    assert token_farm.getStakeholderTokenValue(users[1], weth) == 10 * 2000 * 1e18
    assert token_farm.getStakeholderTokenValue(users[1], fau) == 2 * 1e18

    token_farm.unstake(weth, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[0], weth)
        token_farm.getStakeholderTokenValue(users[0], fau)
    assert token_farm.getStakeholderTokenValue(users[1], weth) == 0
    assert token_farm.getStakeholderTokenValue(users[1], fau) == 2 * 1e18

    token_farm.unstake(fau, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTokenValue(users[0], weth)
        token_farm.getStakeholderTokenValue(users[0], fau)
        token_farm.getStakeholderTokenValue(users[1], weth)
        token_farm.getStakeholderTokenValue(users[1], fau)


@unit_test
def test_unstake_decreases_stakeholder_total_value(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert token_farm.getStakeholderTotalValue(users[0]) == 5 * 1e18
    assert token_farm.getStakeholderTotalValue(users[1]) == 20002 * 1e18

    token_farm.unstake(fau, {"from": users[0]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[0])
    assert token_farm.getStakeholderTotalValue(users[1]) == 20002 * 1e18

    token_farm.unstake(weth, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[0])
    assert token_farm.getStakeholderTotalValue(users[1]) == 2 * 1e18

    token_farm.unstake(fau, {"from": users[1]})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.getStakeholderTotalValue(users[0])
        token_farm.getStakeholderTotalValue(users[1])


@unit_test
def test_unstake_all_token_makes_user_non_stakeholder(staked_token_farm, users):
    (token_farm, weth, fau) = staked_token_farm

    token_farm.unstake(weth, {"from": users[0]})
    assert token_farm.isStakeholder(users[0]) == True
    assert token_farm.isStakeholder(users[1]) == True

    token_farm.unstake(fau, {"from": users[0]})
    assert token_farm.isStakeholder(users[0]) == False
    assert token_farm.isStakeholder(users[1]) == True

    token_farm.unstake(weth, {"from": users[1]})
    assert token_farm.isStakeholder(users[0]) == False
    assert token_farm.isStakeholder(users[1]) == True

    token_farm.unstake(fau, {"from": users[1]})
    assert token_farm.isStakeholder(users[0]) == False
    assert token_farm.isStakeholder(users[1]) == False


@unit_test
def test_only_owner_can_give_reward(staked_token_farm, owner, users):
    (token_farm, _, _) = staked_token_farm

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.reward({"from": users[0]})

    token_farm.reward({"from": owner}).wait(1)


@unit_test
def test_rewards_ten_percent_dapp_token_of_total_value_to_all_stakeholders(
    staked_token_farm, owner, users, dapp_token
):
    (token_farm, _, _) = staked_token_farm

    token_farm.reward({"from": owner}).wait(1)

    assert dapp_token.balanceOf(owner) == 75993 * 1e17
    assert dapp_token.balanceOf(users[0]) == 3005 * 1e17
    assert dapp_token.balanceOf(users[1]) == 21002 * 1e17
