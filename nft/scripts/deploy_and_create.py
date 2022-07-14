from brownie import SimpleCollectible
from scripts.helpers import get_account

sample_token_uri = (
    "ipfs://Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
)

opensea_url = "https://testnets.opensea.io/assets/{}/{}"


def deploy_and_create():
    account = get_account()
    simple_collectible = SimpleCollectible.deploy({"from": account})
    tx = simple_collectible.create(sample_token_uri, {"from": account})
    tx.wait(1)
    token_id = tx.return_value
    nft_opensea_url = opensea_url.format(simple_collectible.address, token_id)
    print(f"View on: {nft_opensea_url}")
    return simple_collectible


def main():
    deploy_and_create()
