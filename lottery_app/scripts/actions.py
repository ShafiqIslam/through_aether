import time
from scripts.helpers import get_account
from brownie import Lottery


def start():
    account = get_account()
    lottery = Lottery[-1]
    lottery.start({"from": account})


def join():
    account = get_account()
    lottery = Lottery[-1]
    lottery.join({"from": account, "value": lottery.getEntryFeeInWei()})


def end():
    account = get_account()
    lottery = Lottery[-1]
    lottery.end({"from": account})
    time.sleep(60)
    print(f"Winner is: {lottery.winner()}")


def main():
    start()
    join()
    end()
