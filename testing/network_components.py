import subprocess
import shutil
import time
import json
import os
import asyncio
from concurrent.futures import TimeoutError

from testing.config_templates import lnd_config_template

dir_path = os.path.dirname(os.path.realpath(__file__))


def decode_byte_to_json(out):
    try:
        json_data = json.loads(out)
        return json_data
    except json.decoder.JSONDecodeError:
        return None


class RegTestBitcoind(object):
    def __init__(self):
        self.conf = os.path.join(dir_path, 'bitcoin/bitcoin.conf')
        self.datadir = os.path.join(dir_path, 'bitcoin')
        self.bitcoincli_command = ['bitcoin-cli']

    def start(self, from_scratch=True):
        if from_scratch:
            self.clear_directory()
        command = ['bitcoind', f'-datadir={self.datadir}']
        print(' '.join(command))
        self.bitcoind = subprocess.Popen(command)
        time.sleep(5.0)  # give bitcoind some time to start

    def stop(self):
        proc = subprocess.run(
            ['bitcoin-cli', 'stop'],
            stdout=subprocess.PIPE,
        )
        if proc.returncode != 0:
            print("bitcoin-cli returned", proc.returncode)
            self.bitcoind.kill()
        print("terminated bitcoind")

    def clear_directory(self):
        print("Cleaning up bitcoin data directory.")
        try:
            shutil.rmtree(os.path.join(dir_path, 'bitcoin', 'blocks'))
            shutil.rmtree(os.path.join(dir_path, 'bitcoin', 'regtest'))
        except FileNotFoundError:
            print("Directory already clean.")

    def bitcoincli(self, command):
        cmd = self.bitcoincli_command + command
        print(' '.join(cmd))
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
        )
        return proc

    def getblockchaininfo(self):
        proc = self.bitcoincli(['getblockchaininfo'])
        return decode_byte_to_json(proc.stdout)

    def get_blockheight(self):
        blockchaininfo = self.getblockchaininfo()
        return blockchaininfo['blocks']

    def mine_blocks(self, number_of_blocks):
        command = list(['generate', str(number_of_blocks)])
        self.bitcoincli(command)

    def sendtoaddress(self, address, amt_btc):
        proc = subprocess.run(
            ['bitcoin-cli', 'sendtoaddress', address, str(amt_btc)],
            stdout=subprocess.PIPE,
        )

    def sendtoadresses(self, addresses, amt_btc):
        for a in addresses:
            self.sendtoaddress(a, amt_btc)


class RegTestLND(object):
    def __init__(self, name, grpc_port, rest_port, port):
        self.name = name
        self.lnd_path = os.path.join(dir_path, 'bin/lnd')
        self.lncli_path = os.path.join(dir_path, 'bin/lncli')
        self.lnddir = os.path.join(dir_path, f'lndnodes/{self.name}')
        self.configfile = os.path.join(dir_path, f'lndnodes/{self.name}/lnd.conf')
        self.rpcport = grpc_port
        self.lndport = port
        self.restport = rest_port
        self.lncli_command = [
            self.lncli_path,
            f'--lnddir={self.lnddir}',
            f'--rpcserver=localhost:{grpc_port}',
            f'--macaroonpath={self.lnddir}/data/chain/bitcoin/regtest/admin.macaroon'
        ]
        self.version=None
        self.pubkey=None

    def print_lncli_command(self):
        cmd = ' '.join(self.lncli_command)
        print(self.name, cmd)

    def setup_lnddir(self):
        os.mkdir(self.lnddir)
        config = lnd_config_template.format(
            lnd_port=self.lndport, rest_port=self.restport, rpc_port=self.rpcport)
        config_path = os.path.join(self.lnddir, 'lnd.conf')
        with open(config_path, 'w') as f:
            f.write(config)

    def clear_directory(self):
        print("Cleaning up lnd data directory.")
        try:
            shutil.rmtree(self.lnddir)
        except FileNotFoundError:
            print("Directory already clean.")

    async def start(self, from_scratch=True):
        if from_scratch:
            self.clear_directory()
            self.setup_lnddir()
        command = [self.lnd_path,
                   f'--lnddir={self.lnddir}',
                   '--noseedbackup']
        cmd = ' '.join(command)
        print(cmd)

        self.lnd = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        while True:
            data = await self.lnd.stdout.readline()
            if data:
                print(self.name, data)
            if 'Finished rescan' in data.decode('utf-8'):
                break

        print(f'lnd {self.name} started')
        await self.init_info()

    async def lncli(self, command):
        cmd = list(self.lncli_command)
        cmd.extend(command)
        print(self.name, 'exec', cmd)
        cmd = ' '.join(map(str, cmd))
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        result = await proc.communicate()
        return decode_byte_to_json(result[0])

    async def init_info(self):
        info = await self.getinfo()
        self.pubkey = info['identity_pubkey']
        print(self.name, self.pubkey)
        self.version = info['version']

    async def getinfo(self):
        return await self.lncli(['getinfo'])

    async def newaddress(self):
        result = await self.lncli(['newaddress', 'p2wkh'])
        address = result['address']
        return address

    async def connect(self, node_pubkey, ip, port):
        command = ['connect', f'{node_pubkey}@{ip}:{port}']
        return await self.lncli(command)

    async def openchannel(self, node_pubkey, amt_sat, amt_push):
        command = ['openchannel', node_pubkey, amt_sat, amt_push]
        return await self.lncli(command)

    async def stop(self):
        try:
            return_value = await asyncio.wait_for(self.lncli(['stop']), 5)
        except TimeoutError:
            print(self.name, "stopping timed out, killing")
            self.lnd.kill()
        print(self.name, 'stopped lnd')


if __name__ == '__main__':
    bitcoind = RegTestBitcoind()
    lnd = RegTestLND('A')
    run_console = False

    try:
        bitcoind.start()
        print(bitcoind.getblockchaininfo())
        print(bitcoind.get_blockheight())
        print(bitcoind.mine_blocks(20))
        print(bitcoind.get_blockheight())

        lnd.start()
    finally:
        if not run_console:
            lnd.stop()
            bitcoind.stop()
