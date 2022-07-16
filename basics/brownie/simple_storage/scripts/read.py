from brownie import SimpleStorage


def read_value_from_previously_deployed_contract():
    simple_storage = SimpleStorage[-1]
    print(simple_storage.retrieve())


def main():
    read_value_from_previously_deployed_contract()
