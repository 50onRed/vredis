#!/usr/bin/env python
import redis
import re

redis_data = {}

class MockConnectionPool(object):
    def __init__(self, connection_class=redis.Connection, 
                 max_connections=None, **connection_kwargs):
        self.server_str = "%s:%s" % (connection_kwargs['host'], connection_kwargs['port'])
        redis_data[self.server_str] = {}
        self.connection = None
    
    def release(self, connection):
        self.connection = None
        
    def get_connection(self, command_name, *keys, **options):
        if self.connection is None:
            self.connection = MockConnection(self.server_str)
        return self.connection

class MockConnection(object):
    def __init__(self, server_str, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, encoding='utf-8',
                 encoding_errors='strict', parser_class=redis.connection.PythonParser):
        self.server_str = server_str
        self.last_result = None
    
    def send_command(self, *args):
        if args[0] == "SET":
            redis_data[self.server_str][args[1]] = args[2]
            self.last_result = "OK"
        elif args[0] == "MSET":
            redis_data[self.server_str].update(zip(args[1::2], args[0::2][1:]))
            self.last_result = "OK"
        elif args[0] == "GET":
            self.last_result = redis_data[self.server_str][args[1]]
        elif args[0] == "MGET":
            self.last_result = [redis_data[self.server_str][x] if x in redis_data[self.server_str] else None for x in args[1:]]
        elif args[0] == "KEYS":
            pattern = args[1].replace("*", ".*") # quick hack
            self.last_result = [x if re.match(pattern, x) else None for x in redis_data[self.server_str]]
        elif args[0] == "DBSIZE":
            self.last_result = len(redis_data[self.server_str])
        elif args[0] == "FLUSHALL":
            redis_data[self.server_str] = {}
            self.last_result = "OK"
    
    def read_response(self):
        return self.last_result
