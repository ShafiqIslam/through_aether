import json
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("./compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

w3 = Web3(Web3.HTTPProvider(os.getenv("CHAIN_PROVIDER_URL")))
chain_id = int(os.getenv("CHAIN_ID"))
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("MY_PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)


def get_transaction_build_params():
    return {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": w3.eth.getTransactionCount(my_address),
    }


def get_signed_transaction(builder):
    transaction = builder.build_transaction(get_transaction_build_params())
    return w3.eth.account.sign_transaction(transaction, private_key=private_key)


def send_transaction_and_get_receipt(builder):
    signed_transaction = get_signed_transaction(builder)
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(transaction_hash)


print("Deploying contract...")
contract_creation_transaction_receipt = send_transaction_and_get_receipt(
    SimpleStorage.constructor()
)
print("Contract deployed.")

simple_storage = w3.eth.contract(
    address=contract_creation_transaction_receipt.contractAddress, abi=abi
)

print("Retrive on contract: ", simple_storage.functions.retrieve().call())


print("Store a transaction by the contract...")
transaction_receipt = send_transaction_and_get_receipt(
    simple_storage.functions.store(10)
)
print("Tranaction stored.")

print("Retrive on contract: ", simple_storage.functions.retrieve().call())
