lnd_config_template = \
    "[Application Options]\n" \
    "listen=localhost:{lnd_port}\n" \
    "restlisten=localhost:{rest_port}\n" \
    "rpclisten=localhost:{rpc_port}\n" \
    "debuglevel=debug\n" \
    "[Bitcoin]\n" \
    "bitcoin.active=1\n" \
    "bitcoin.regtest=1\n" \
    "bitcoin.node=bitcoind\n" \
    "[Bitcoind]\n" \
    "bitcoind.rpchost=localhost\n" \
    "bitcoind.rpcuser=lnd\n" \
    "bitcoind.rpcpass=123456\n" \
    "bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332\n" \
    "bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333"
