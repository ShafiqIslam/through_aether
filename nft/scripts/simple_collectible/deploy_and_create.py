from brownie import SimpleCollectible
from scripts.helpers import get_account, get_open_sea_url

sample_token_uri = (
    "ipfs://Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
)


def deploy_and_create():
    account = get_account()
    simple_collectible = SimpleCollectible.deploy({"from": account})
    tx = simple_collectible.create(sample_token_uri, {"from": account})
    tx.wait(1)
    token_id = tx.return_value
    nft_opensea_url = get_open_sea_url(simple_collectible, token_id)
    print(f"View on: {nft_opensea_url}")
    return simple_collectible


def main():
    deploy_and_create()
