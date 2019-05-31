nodes = {
    'A': {
        'grpc_port': 11009,
        'rest_port': 8080,
        'port': 9735,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'B',
                'capacity': 4000000,
                'ratio_local': 10,
                'ratio_remote': 9,
            },
            2: {
                'to': 'C',
                'capacity': 5000000,
                'ratio_local': 10,
                'ratio_remote': 9,
            },
            3: {
                'to': 'D',
                'capacity': 6000000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
            4: {
                'to': 'E',
                'capacity': 1000000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
        }
    },
    'B': {
        'grpc_port': 11010,
        'rest_port': 8081,
        'port': 9736,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'C',
                'capacity': 100000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
            2: {
                'to': 'F',
                'capacity': 2000000,
                'ratio_local': 9,
                'ratio_remote': 1,
            },
        }
    },
    'C': {
        'grpc_port': 11011,
        'rest_port': 8082,
        'port': 9737,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'G',
                'capacity': 500000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
        }
    },
    'D': {
        'grpc_port': 11012,
        'rest_port': 8083,
        'port': 9738,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'C',
                'capacity': 1000000,
                'ratio_local': 7,
                'ratio_remote': 3,
            },
            2: {
                'to': 'G',
                'capacity': 7000000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
        }
    },
    'E': {
        'grpc_port': 11013,
        'rest_port': 8084,
        'port': 9739,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'B',
                'capacity': 2000000,
                'ratio_local': 9,
                'ratio_remote': 1,
            },
            2: {
                'to': 'D',
                'capacity': 300000,
                'ratio_local': 6,
                'ratio_remote': 5,
            },
            3: {
                'to': 'H',
                'capacity': 4000000,
                'ratio_local': 6,
                'ratio_remote': 4,
            },
        }
    },
    'F': {
        'grpc_port': 11014,
        'rest_port': 8085,
        'port': 9740,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'C',
                'capacity': 3000000,
                'ratio_local': 9,
                'ratio_remote': 1,
            },
        }
    },
    'G': {
        'grpc_port': 11015,
        'rest_port': 8086,
        'port': 9741,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'A',
                'capacity': 3000000,
                'ratio_local': 9,
                'ratio_remote': 1,
            },
        }
    },
    'H': {
        'grpc_port': 11016,
        'rest_port': 8087,
        'port': 9742,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'D',
                'capacity': 700000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
        }
    },
    'I': {
        'grpc_port': 11017,
        'rest_port': 8088,
        'port': 9743,
        'base_fee': 1.000000,
        'fee_rate': 0.000001,
        'channels': {
            1: {
                'to': 'B',
                'capacity': 300000,
                'ratio_local': 10,
                'ratio_remote': 0,
            },
            2: {
                'to': 'E',
                'capacity': 10000000,
                'ratio_local': 10,
                'ratio_remote': 1,
            },
        }
    },
}
