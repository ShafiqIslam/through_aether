from brownie import AdvancedCollectible
from scripts.helpers import get_open_sea_url, get_account

metadata_links = {
    "PUG": "ipfs://Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json",
    "SHIBA_INU": "ipfs://QmdryoExpgEQQQgJPoruwGJyZmz6SqV4FRTX1i73CT3iXn?filename=1-SHIBA_INU.json",
    "ST_BERNARD": "ipfs://QmbBnUjyHHN7Ytq9xDsYF9sucZdDJLRkWz7vnZfrjMXMxs?filename=2-ST_BERNARD.json",
}


def set_token_uri(collectible, token_id):
    breed = collectible.getBreedNameOf(token_id)
    collectible.setTokenURI(token_id, metadata_links[breed], {"from": get_account()})
    print(
        "Awesome! You can view your NFT at {}".format(
            get_open_sea_url(collectible, token_id)
        )
    )


def does_not_have_uri(collectible, token_id):
    return not collectible.tokenURI(token_id).startswith("https://")


def set_all_token_uri():
    advanced_collectible = AdvancedCollectible[-1]
    token_count = advanced_collectible.getTokenCount()
    for i in range(token_count):
        if does_not_have_uri(advanced_collectible, i):
            set_token_uri(advanced_collectible, i)


def main():
    set_all_token_uri()
