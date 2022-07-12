import time
from scripts.deploy import deploy
from scripts.helpers import get_account, is_local_network
import pytest


def test_full_lottery():
    if is_local_network():
        pytest.skip()

    lottery = deploy()
    lottery.start({"from": get_account()})
    lottery.join({"from": get_account(), "value": lottery.getEntryFeeInWei()})

    expected_new_balance = lottery.balance() + get_account().balance()

    lottery.end({"from": get_account()})
    time.sleep(60)

    assert lottery.winner() == get_account().address
    assert lottery.balance() == 0
    assert get_account().balance() == expected_new_balance
    assert lottery.getStatus() == "Closed"
