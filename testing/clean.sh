killall -9 bitcoind
killall -9 lnd
rm -rf bitcoin/blocks bitcoin/regtest
cd lndnodes/A
rm -rf data  graph  logs  tls.cert  tls.key
