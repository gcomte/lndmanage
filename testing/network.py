import time
import asyncio

from testing.network_components import RegTestLND, RegTestBitcoind
from testing.network_definitions import nodes as nodes

NODE_LIMIT = 'F'
FROM_SCRATCH = True


class RegtestNetwork(object):
    def __init__(self):

        self.bitcoind = RegTestBitcoind()
        self.lnd_nodes = {k: RegTestLND(
            name=k,
            grpc_port=v['grpc_port'],
            rest_port=v['rest_port'],
            port=v['port']
        )
            for k, v in nodes.items()}
        self.loop = asyncio.get_event_loop()

    def run(self):
        try:
            self.bitcoind.start(from_scratch=FROM_SCRATCH)
            self.loop.run_until_complete(self.init_lnd_nodes(from_scratch=FROM_SCRATCH))
            time.sleep(5)

            if FROM_SCRATCH:
                self.fill_lnd_wallets(number_of_times=3)
                time.sleep(5)  # TODO: cleaner way to wait for lnds to synchronize
                self.loop.run_until_complete(self.connect_and_open_channels())
                self.bitcoind.mine_blocks(20)
                time.sleep(5)

            for status in self.loop.run_until_complete(self.lnd_nodes_getinfo()):
                print(status)

            print('Local lightning network is set up. Have fun.')
            self.print_lncli_commands()

            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            #self.loop.run_until_complete(self.stop_lnd_nodes())
            self.stop_lnd_nodes_serially()
            self.loop.close()
            self.bitcoind.stop()

    def print_lncli_commands(self):
        print('lncli commands:')
        for k, v in self.lnd_nodes.items():
            v.print_lncli_command()

    async def init_lnd_nodes(self, from_scratch):
        tasks = [v.start(from_scratch) for k, v in self.lnd_nodes.items() if k < NODE_LIMIT]
        await asyncio.gather(*tasks, loop=self.loop)

    async def lnd_nodes_getinfo(self):
        tasks = [v.getinfo() for k, v in self.lnd_nodes.items() if k < NODE_LIMIT]
        return await asyncio.gather(*tasks, loop=self.loop)

    async def stop_lnd_nodes(self):
        tasks = [v.stop() for k, v in self.lnd_nodes.items() if k < NODE_LIMIT]
        await asyncio.gather(*tasks, loop=self.loop)

    def stop_lnd_nodes_serially(self):
        for k, v in self.lnd_nodes.items():
                if k < NODE_LIMIT:
                    self.loop.run_until_complete(v.stop())

    async def generate_addresses(self):
        print('generating addresses')
        tasks = [v.newaddress() for k, v in self.lnd_nodes.items() if k < NODE_LIMIT]
        addresses = await asyncio.gather(*tasks, loop=self.loop)
        return addresses

    def fill_lnd_wallets(self, number_of_times):
        for _ in range(number_of_times):
            print('filling lnd wallets')
            print(self.bitcoind.mine_blocks(110))
            # generated addresses and fill the nodes' wallets
            addresses = self.loop.run_until_complete(self.generate_addresses())
            print('addresses', addresses)
            self.bitcoind.sendtoadresses(addresses, 1.0)
            print('blocks mined', self.bitcoind.mine_blocks(6))

    async def connect_and_open_channels_for_node(self, node_name):
        print('connecting node', node_name)
        for channel, channel_data in nodes[node_name]['channels'].items():
            node_to_connect = channel_data['to']
            if node_to_connect >= NODE_LIMIT:
                continue
            node_pub_key = self.lnd_nodes[node_to_connect].pubkey
            node_port = self.lnd_nodes[node_to_connect].lndport
            await self.lnd_nodes[node_name].connect(node_pub_key, 'localhost', node_port)

        print('opening channels node', node_name)
        for channel, channel_data in nodes[node_name]['channels'].items():
            node_to_connect = channel_data['to']
            if node_to_connect >= NODE_LIMIT:
                continue
            node_pub_key = self.lnd_nodes[node_to_connect].pubkey
            capacity = channel_data['capacity']
            total_relative = (channel_data['ratio_local'] + channel_data['ratio_remote'])

            local_relative = float(channel_data['ratio_local']) / total_relative
            remote_relative = float(channel_data['ratio_remote']) / total_relative

            local_amt = int(capacity * local_relative)
            remote_amt = int(capacity * remote_relative)

            await self.lnd_nodes[node_name].openchannel(node_pub_key, local_amt, remote_amt)

    async def connect_and_open_channels(self):
        print('connecting nodes')
        tasks = []
        for node_name, node_object in self.lnd_nodes.items():
            if node_name >= NODE_LIMIT:
                continue
            tasks.append(self.connect_and_open_channels_for_node(node_name))
        connection = await asyncio.gather(*tasks, loop=self.loop)
        time.sleep(5)
        print('connect', connection)
        self.bitcoind.mine_blocks(6)

        return connection


if __name__ == '__main__':
    network = RegtestNetwork()
    network.run()
