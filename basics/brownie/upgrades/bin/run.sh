# run test on local
brownie test

# run on testnet
brownie run scripts/deploy.py --network rinkeby
brownie run scripts/upgrade.py --network rinkeby
brownie run scripts/interact.py --network rinkeby