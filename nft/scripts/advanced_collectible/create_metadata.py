import json
from brownie import AdvancedCollectible, config, network
from metadata.boilerplate import metadata_boilerplate
import requests
from pathlib import Path


def get_metadata_file_name(token_id, breed):
    return "./metadata/{}/{}-{}.json".format(network.show_active(), token_id, breed)


def does_metadata_file_exists(token_id, breed):
    return Path(get_metadata_file_name(token_id, breed)).exists()


def get_image_path(breed):
    return "./img/{}.png".format(breed.lower().replace("_", "-"))


def upload_breed_image_to_ipfs_and_get_url(breed):
    return upload_file_to_ipfs_and_get_url(get_image_path(breed))


def save_metadata_file_and_upload_to_ipfs(token_id, breed, metadata):
    metadata_file_name = get_metadata_file_name(token_id, breed)
    with open(metadata_file_name, "w") as file:
        json.dump(metadata, file)
    upload_file_to_ipfs_and_get_url(metadata_file_name)


def add_to_local_ipfs_and_get_qm_hash(file_binary):
    response = requests.post(
        config["ipfs_url"] + "/api/v0/add", files={"file": file_binary}
    )
    return response.json()["Hash"]


def pin_to_pinata(file_binary, filename):
    requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={"file": (filename, file_binary)},
        headers={
            "pinata_api_key": config["pinata"]["api_key"],
            "pinata_secret_api_key": config["pinata"]["api_secret"],
        },
    )


def upload_file_to_ipfs_and_get_url(filepath):
    filename = filepath.split("/")[-1:][0]

    with Path(filepath).open("rb") as fp:
        file_binary = fp.read()
        ipfs_hash = add_to_local_ipfs_and_get_qm_hash(file_binary)
        pin_to_pinata(file_binary, filename)

    return "ipfs://{}?filename={}".format(ipfs_hash, filename)


def build_metadata(breed):
    metadata = metadata_boilerplate
    metadata["name"] = breed
    metadata["description"] = "An adorable {} pup!".format(breed)
    metadata["image"] = upload_breed_image_to_ipfs_and_get_url(breed)
    return metadata


def create_metadata_of_token(token_id, breed):
    if does_metadata_file_exists(token_id, breed):
        return

    metadata = build_metadata(breed)
    save_metadata_file_and_upload_to_ipfs(token_id, breed, metadata)


def create_metadata():
    advanced_collectible = AdvancedCollectible[-1]
    token_count = advanced_collectible.getTokenCount()
    for i in range(token_count):
        breed = advanced_collectible.getBreedNameOf(i)
        create_metadata_of_token(i, breed)


def main():
    create_metadata()
