brownie networks delete mainnet-fork
brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 \
    fork=https://eth-mainnet.g.alchemy.com/v2/bIqpeD5Lkevft9EqlVyg1pj_qEPZq3Ae \
    accounts=10 mnemonic=brownie port=8545