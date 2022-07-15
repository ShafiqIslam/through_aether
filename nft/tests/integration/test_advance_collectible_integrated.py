from scripts.helpers import is_dev_network, get_account
from scripts.advanced_collectible.deploy import deploy
from scripts.advanced_collectible.create_token import create_token
import pytest
import time


def test_advanced_collectible_integrated():
    if is_dev_network():
        pytest.skip()

    collectible = deploy()
    create_token(get_account())
    time.sleep(60)

    assert collectible.getTokenCount() == 1
    assert collectible.ownerOf(0) == get_account()
