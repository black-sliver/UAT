#!/usr/bin/python3

import sys, argparse, json, unittest
from jsonschema import validate
from pathlib import Path

from_server_commands = ['Info', 'Var', 'ErrorReply']
from_client_commands = ['Sync']
test_data_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "from": {"type": "string", "enum": ["client","server"]},
            "expect": {"type": "string", "enum": ["success", "fail", "strict-fail"]},
            "packet": {}
        },
        "required": ["from", "expect", "packet"]
    }
}


def make_packet_test(packet_schema, commands_schema, data, expect, name='', description=''):
    def __init__(self):
        unittest.TestCase.__init__(self,name)

    def test_packet(self):
        try:
            validate(instance = data, schema = packet_schema)
            for command in data:
                if command["cmd"] in commands_schema:
                    validate(instance = command, schema = commands_schema[command["cmd"]])
        except Exception as ex:
            if expect == 'fail':
                return
            raise ex
        if expect == 'fail':
            raise Exception(f'{name} was supposed to fail validation')

    return type('PacketTest', (unittest.TestCase,), {
        '__init__': __init__,
        name: test_packet,
        '__doc__': f'{name}: {description}'
    })()


def main(args):
    schema_dir = Path(args.schema)
    data_dir = Path(args.data)
    with (schema_dir / 'packet.json').open() as f:
        packet_schema = json.load(f)
    from_server_schema = {}
    from_client_schema = {}
    for cmd in from_server_commands:
        with (schema_dir / (cmd + '.json')).open() as f:
            from_server_schema[cmd] = json.load(f)
    for cmd in from_client_commands:
        with (schema_dir / (cmd + '.json')).open() as f:
            from_client_schema[cmd] = json.load(f)
    
    suite = unittest.TestSuite()
    for data_file in sorted(data_dir.iterdir()):
        with data_file.open() as f:
            print(f'Creating test cases from {data_file}')
            data = json.load(f)
            validate(instance = data, schema = test_data_schema)
            for i, test in enumerate(data):
                commands_schema = from_server_schema if test['from'] == 'server' else from_client_schema
                suite.addTest(make_packet_test(packet_schema, commands_schema,
                              test['packet'], test['expect'], f'{data_file.name}[{i}]'))

    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate UAT data against UAT schema')
    parser.add_argument('-s', '--schema-dir', dest='schema', default='../schema/UAT',
                        help='directory for schema (default: %(default)s)')
    parser.add_argument('-d', '--data-dir', dest='data', default='./data',
                        help='directory for data (default: %(default)s)')
    main(parser.parse_args())
