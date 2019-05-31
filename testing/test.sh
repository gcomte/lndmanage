#!/bin/bash

## start bitcoind in regtest mode
#bitcoind -datadir=`pwd`/bitcoin
#bitcoin-cli generate 100
#
#bitcoin-cli getblockchaininfo
#bitcoin-cli getbalance
#
#
## start up lnd instances
mkdir -p lndnodes/A
mkdir -p lndnodes/B
mkdir -p lndnodes/C

echo "[Application Options]

listen=0.0.0.0:9735
rpclisten=localhost:11009
restlisten=0.0.0.0:8080

[Bitcoin]

bitcoin.active=1
bitcoin.regtest=1
bitcoin.node=bitcoind

[Bitcoind]

bitcoind.rpchost=localhost
bitcoind.rpcuser=lnd
bitcoind.rpcpass=123456
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
" > ./lndnodes/A/lnd.conf

echo "[Application Options]

listen=0.0.0.0:9736
rpclisten=localhost:11010
restlisten=0.0.0.0:8081

[Bitcoin]

bitcoin.active=1
bitcoin.regtest=1
bitcoin.node=bitcoind

[Bitcoind]

bitcoind.rpchost=localhost
bitcoind.rpcuser=lnd
bitcoind.rpcpass=123456
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
" > ./lndnodes/B/lnd.conf

echo "[Application Options]

listen=0.0.0.0:9737
rpclisten=localhost:11011
restlisten=0.0.0.0:8082

[Bitcoin]

bitcoin.active=1
bitcoin.regtest=1
bitcoin.node=bitcoind

[Bitcoind]

bitcoind.rpchost=localhost
bitcoind.rpcuser=lnd
bitcoind.rpcpass=123456
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
" > ./lndnodes/C/lnd.conf

bin/lnd --lnddir=./lndnodes/A --noseedbackup > A
bin/lnd --lnddir=./lndnodes/B --noseedbackup > B
bin/lnd --lnddir=./lndnodes/C --noseedbackup > C
clear
echo "LNDs are running!"

alias lna="bin/lncli --lnddir=./lndnodes/A --rpcserver=127.0.0.1:11009 --network regtest getinfo"
alias lnb="bin/lncli --lnddir=./lndnodes/B --rpcserver=127.0.0.1:11010 --network regtest getinfo"
alias lnc="bin/lncli --lnddir=./lndnodes/C --rpcserver=127.0.0.1:11011 --network regtest getinfo"

exit 

LNCLI="$HOME/lightninglabs/lnd/lncli-debug --no-macaroons"

CLI_ALICE="$HOME/lightninglabs/lnd/lncli-debug --network=regtest"
CLI_BOB="$HOME/lightninglabs/lnd/lncli-debug --network=regtest --macaroonpath ~/.lnd-bob/data/chain/bitcoin/regtest/admin.macaroon --rpcserver=localhost:10002"
CLI_CHARLIE="$HOME/lightninglabs/lnd/lncli-debug --network=regtest --macaroonpath ~/.lnd-charlie/data/chain/bitcoin/regtest/admin.macaroon --rpcserver=localhost:10003"

ALICE=`$CLI_ALICE getinfo | jq .identity_pubkey -r`
BOB=`$CLI_BOB getinfo | jq .identity_pubkey -r`
CHARLIE=`$CLI_CHARLIE getinfo | jq .identity_pubkey -r`

ADDR_ALICE=`$CLI_ALICE newaddress p2wkh | jq .address -r`
ADDR_BOB=`$CLI_BOB newaddress p2wkh | jq .address -r`

bitcoin-cli sendtoaddress $ADDR_ALICE 1
bitcoin-cli sendtoaddress $ADDR_BOB 1

bitcoin-cli generate 6

$CLI_ALICE connect $BOB@localhost:10012
$CLI_ALICE connect $CHARLIE@localhost:10013

$CLI_ALICE openchannel $BOB 10000000 5000000

bitcoin-cli generate 6

$CLI_ALICE openchannel $CHARLIE 10000000 5000000

bitcoin-cli generate 6


