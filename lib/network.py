import _settings
import os
import time
import pickle

import networkx as nx

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Network(object):
    """
    Contains the network graph. The graph is received from the LND API or from a cached file,
    which contains the graph younger than `settings.CACHING_RETENTION_MINUTES`.

    :param node: :class:`lib.node.LndNode` object
    """

    def __init__(self, node):
        logger.info("Initializing network graph.")
        self.node = node
        self.edges = {}
        self.graph = nx.MultiDiGraph()
        self.cached_reading_graph_edges()

    def cached_reading_graph_edges(self):
        """
        Checks if networkx and edges dictionary pickles are present. If they are older than
        CACHING_RETENTION_MINUTES, make fresh pickles, else read them from the files.
        """
        dir = os.path.dirname(__file__)
        cache_edges_filename = os.path.join(dir, '..', 'cache', 'graph.gpickle')
        cache_graph_filename = os.path.join(dir, '..', 'cache', 'edges.gpickle')

        try:
            timestamp_graph = os.path.getmtime(cache_graph_filename)
        except FileNotFoundError:
            timestamp_graph = 0  # set very old timestamp

        if timestamp_graph < time.time() - _settings.CACHING_RETENTION_MINUTES * 60:  # old graph in file
            logger.info(f"Saved graph is too old. Fetching new one.")
            self.set_graph_and_edges()
            nx.write_gpickle(self.graph, cache_graph_filename)
            with open(cache_edges_filename, 'wb') as file:
                pickle.dump(self.edges, file)
        else:  # recent graph in file
            logger.info("Reading graph from file.")
            self.graph = nx.read_gpickle(cache_graph_filename)
            with open(cache_edges_filename, 'rb') as file:
                self.edges = pickle.load(file)

    def set_graph_and_edges(self):
        """
        Reads in the networkx graph and edges dictionary.
        :return: nx graph and edges dict
        """
        raw_graph = self.node.get_raw_network_graph()

        for n in raw_graph.nodes:
            if n.addresses:
                # TODO: handle also ipv6 and onion addresses
                address = n.addresses[0].addr
                if 'onion' in address or '[' in address:
                    address = ''
            else:
                address = ''

            self.graph.add_node(
                n.pub_key,
                alias=n.alias,
                last_update=n.last_update,
                address=address,
                color=n.color)

        for e in raw_graph.edges:
            # TODO refactor out grpc file format
            # create a dictionary for channel_id lookups
            self.edges[e.channel_id] = {
                'node1_pub': e.node1_pub,
                'node2_pub': e.node2_pub,
                'capacity': e.capacity,
                'last_update': e.last_update,
                'channel_id': e.channel_id,
                'node1_policy': {
                    'time_lock_delta': e.node1_policy.time_lock_delta,
                    'fee_base_msat': e.node1_policy.fee_base_msat,
                    'fee_rate_milli_msat': e.node1_policy.fee_rate_milli_msat,
                    'disabled': e.node1_policy.disabled
                },
                'node2_policy': {
                    'time_lock_delta': e.node2_policy.time_lock_delta,
                    'fee_base_msat': e.node2_policy.fee_base_msat,
                    'fee_rate_milli_msat': e.node2_policy.fee_rate_milli_msat,
                    'disabled': e.node2_policy.disabled
                }}

            # add vertices to network graph for edge-based lookups
            self.graph.add_edge(
                e.node2_pub,
                e.node1_pub,
                channel_id=e.channel_id,
                last_update=e.last_update,
                capacity=e.capacity,
                fees={
                    'time_lock_delta': e.node2_policy.time_lock_delta,
                    'fee_base_msat': e.node2_policy.fee_base_msat,
                    'fee_rate_milli_msat': e.node2_policy.fee_rate_milli_msat,
                    'disabled': e.node2_policy.disabled
                })
            self.graph.add_edge(
                e.node1_pub,
                e.node2_pub,
                channel_id=e.channel_id,
                last_update=e.last_update,
                capacity=e.capacity,
                fees={
                    'time_lock_delta': e.node1_policy.time_lock_delta,
                    'fee_base_msat': e.node1_policy.fee_base_msat,
                    'fee_rate_milli_msat': e.node1_policy.fee_rate_milli_msat,
                    'disabled': e.node1_policy.disabled
                })

    def number_channels(self, node_pub_key):
        """
        Determines the degree of a given node.
        :param node_pub_key: str
        :return: int
        """
        try:
            number_of_channels = self.graph.degree[node_pub_key] / 2
        except KeyError:
            number_of_channels = 0
        return number_of_channels

    def node_capacity(self, node_pub_key):
        """
        Calculates the total capacity of a node in satoshi.
        :param node_pub_key: str
        :return: int
        """
        total_capacity = 0
        edges = self.graph.edges(node_pub_key, data=True)
        for e in edges:
            total_capacity += e[2]['capacity']
        return total_capacity

    def node_alias(self, node_pub_key):
        """
        Wrapper to get the alias of a node given its public key.
        :param node_pub_key:
        :return: alias string
        """
        try:
            return self.graph.node[node_pub_key]['alias']
        except KeyError:
            return 'unknown alias'

    def node_address(self, node_pub_key):
        """
        Returns the IP/onion addresses of a node.
        :param node_pub_key:
        :return: list
        """
        return self.graph.node[node_pub_key]['address']

    def neighbors(self, node_pub_key):
        """
        Finds all the node pub keys of nearest neighbor nodes
        :param node_pub_key:  str
        :return: node_pub_key: str
        """
        neighbors = nx.neighbors(self.graph, node_pub_key)
        for n in neighbors:
            yield n

    def second_neighbors(self, node_pub_key):
        """
        Finds all the node pub keys of second nearest neighbor nodes (non-unique)
        :param node_pub_key: str
        :return: node_pub_key: str
        """
        for neighbor_list in [self.graph.neighbors(n) for n in self.graph.neighbors(node_pub_key)]:
            for n in neighbor_list:
                yield n

    def nodes_in_neighborhood_of_nodes(self, nodes, blacklist_nodes, limit=100):
        """
        Takes a list of nodes and finds the neighbors with most connections to the nodes.
        :param nodes: list
        :param blacklist_nodes: list of node_pub_keys to be excluded from counting
        :return: list of tuples, (str pub_key, int number of neighbors)
        """
        nodes = set(nodes)
        # eliminate blacklisted nodes
        nodes = nodes.difference(blacklist_nodes)
        neighboring_nodes = []
        for general_node in self.graph.nodes:
            neighbors_general_node = set(self.neighbors(general_node))
            intersection_with_nodes = nodes.intersection(neighbors_general_node)
            number_of_connection_with_nodes = len(intersection_with_nodes)
            neighboring_nodes.append((general_node, number_of_connection_with_nodes))

        sorted_neighboring_nodes = sorted(neighboring_nodes, key=lambda x: x[1], reverse=True)
        return sorted_neighboring_nodes[:limit]


if __name__ == '__main__':
    import logging.config
    logging.config.dictConfig(_settings.logger_config)

    from lib.node import LndNode
    nd = LndNode()
    print(f"Graph size: {nd.network.graph.size()}")
    print(f"Number of channels: {len(nd.network.edges.keys())}")
