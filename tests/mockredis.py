#!/usr/bin/env python
import redis

class MockConnectionPool(object):
    def __init__(self, connection_class=redis.Connection, 
                 max_connections=None, **connection_kwargs):
        pass
    
    def release(self, connection):
        pass
        
    def get_connection(self, command_name, *keys, **options):
        return MockConnection()

class MockConnection(object):
    data = {}
    last_result = None
    
    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, encoding='utf-8',
                 encoding_errors='strict', parser_class=redis.connection.PythonParser):
        pass
    
    def send_command(self, *args):
        if args[0] == "SET":
            self.data[args[1]] = args[2]
            self.last_result = "OK"
        elif args[0] == "MSET":
            self.data.update(zip(args[1::2], args[0::2][1:]))
            self.last_result = "OK"
        elif args[0] == "GET":
            self.last_result = self.data[args[1]]
        elif args[0] == "MGET":
            self.last_result = [self.data[x] if x in self.data else None for x in args[1:]]
        elif args[0] == "FLUSHALL":
            self.data = {}
            self.last_result = "OK"
    
    def read_response(self):
        return self.last_result
