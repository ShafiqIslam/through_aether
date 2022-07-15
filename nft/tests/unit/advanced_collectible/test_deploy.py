from scripts.helpers import is_not_local_network
from scripts.advanced_collectible.deploy import deploy
import pytest


def test_advanced_collectible_deploy():
    if is_not_local_network():
        pytest.skip()

    collectible = deploy()
    assert collectible.name() == "Dog"
    assert collectible.symbol() == "DOG"
    assert collectible.getTokenCount() == 0
