from web3 import Web3
from brownie import exceptions, accounts
from scripts.dependencies import get_mock_contract
from scripts.helpers import is_not_local_network, get_account
from scripts.deploy import deploy
import pytest


def test_entry_fee():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()

    today_price = 2000
    expected_eth = 10 / today_price
    expected_wei = str(Web3.toWei(expected_eth, "ether"))

    actual_wei = str(lottery.getEntryFeeInWei())

    assert len(actual_wei) == len(expected_wei)
    assert actual_wei[0:2] == expected_wei[0:2]


def test_cant_join_unless_started():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei()})


def test_only_owner_can_start():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.start({"from": accounts[1]})

    lottery.start({"from": get_account()})
    assert lottery.getStatus() == "Open"


def test_can_started_only_in_closed_status():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.start({"from": get_account()})


def test_cant_join_with_wrong_entry_fee():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei() - 100})
        lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei() + 100})


def test_can_join():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})
    lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei()})
    assert lottery.players(0) == get_account().address

    lottery.join({"from": accounts[1], "value": lottery.getEntryFeeInWei()})
    assert lottery.players(1) == accounts[1].address


def test_only_owner_can_end():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.end({"from": accounts[1]})

    lottery.end({"from": get_account()})
    assert lottery.getStatus() == "Calculating Winner"


def test_can_ended_only_in_open_status():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.end({"from": get_account()})

    lottery.start({"from": get_account()})
    lottery.end({"from": get_account()})
    assert lottery.getStatus() == "Calculating Winner"


def test_end_should_choose_winner():
    if is_not_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})
    lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei()})
    lottery.join({"from": accounts[1], "value": lottery.getEntryFeeInWei()})
    lottery.join({"from": accounts[2], "value": lottery.getEntryFeeInWei()})

    expected_new_balance = lottery.balance() + accounts[2].balance()

    end_tx = lottery.end({"from": get_account()})

    get_mock_contract("vrf_coordinator").fulfillRandomWordsWithOverride(
        end_tx.events["RandomNumberRequested"]["requestId"],
        lottery.address,
        [8],
        {"from": get_account()},
    )

    assert lottery.winner() == accounts[2].address
    assert lottery.balance() == 0
    assert accounts[2].balance() == expected_new_balance
    assert lottery.getStatus() == "Closed"
