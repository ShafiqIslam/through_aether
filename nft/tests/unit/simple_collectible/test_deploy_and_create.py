from scripts.helpers import is_not_local_network, get_account
from scripts.simple_collectible.deploy_and_create import deploy_and_create
import pytest


def test_deploy_and_create_simple_collectible():
    if is_not_local_network():
        pytest.skip()

    collectible = deploy_and_create()
    assert collectible.ownerOf(0) == get_account()
