#!/usr/bin/env python
import redis
import hashlib
from redis.exceptions import ConnectionError

class VRedis(redis.Redis):
    """ Provides a client-side vbucket-aware interface to Redis """
    
    def __init__(self, hosts, db=0, socket_timeout=None, 
                 charset='utf-8', errors='strict', 
                 cls=redis.ConnectionPool):
        """ Initialize VRedis object """
        super( VRedis, self ).__init__(db=db, socket_timeout=socket_timeout, 
            charset=charset,errors=errors)
        self.ring = []
        self.hosts = hosts
        self.pools = {}
        for host, port, end_bucket in self.hosts: 
            # initialize a connection pool per host
            self.pools['%s:%d' % (host, port)] = cls(host=host, port=port)

        self.generate_ring()

    def generate_ring(self):
        """ Ring size is 255 by default """
        for host in self.hosts:
            (hostname, port, end_bucket) = host
            self.ring.append(('%s:%d' % (hostname, port), end_bucket))

    @staticmethod
    def hash(message):
        """
        Hashing function that returns an int 0..255
        based on the hash of message
        """
        return int('0x%s' % (hashlib.new('md5', message).hexdigest()[:2]), 16)

    def get_server(self, key):
        """ Return the server host:port string to be used for given key """
        position = self.hash(key)
        for host, limit in self.ring:
            if limit >= position:
                return host

    def mget(self, keys, *args):
        """
        Split the keys into lists per server, 
        execute on each server separately, 
        and combine and return the results
        """
        keys = redis.client.list_or_args(keys, args)
        results = {}
        for key in keys:
            hostkey = self.get_server(key)
            if hostkey in results:
                results[hostkey][key] = None
            else:
                results[hostkey] = {key: None}
        # results looks like: 
        # {"server1": 
        #    {key1: None, key2: None, key3: None},
        #  "server2": 
        #    {key4: None, key5: None, key6: None}
        # } 
        for server, server_data in results.iteritems():
            server_keys = server_data.keys()
            new_args = ["MGET"]
            new_args.extend(server_keys)
            values = self.execute_command_on_server(server, *new_args)
            server_data.update(zip(server_keys, values))
        output = []
        for key in keys:
            for server, server_data in results.iteritems():
                if key in server_data:
                    output.append(server_data[key])
                    break
        return output
    
    def dbsize(self):
        """ Run dbsize on all the servers and return the sum """
        result = 0
        for host, limit in self.ring:
            tmp = self.execute_command_on_server(host, 'DBSIZE')
            result = result + tmp
        return result
    
    def keys(self, pattern='*'):
        """ Run keys on all the servers and return the combines set """
        result = []
        for host, limit in self.ring:
            tmp = self.execute_command_on_server(host, 'KEYS', pattern)
            result.extend(tmp)
        return result
    
    def mset(self, mapping):
        """
        Split the keys into dictionaries per server, 
        execute on each server separately, 
        and return True only if all of the servers returned True
        """
        items = []
        for pair in mapping.iteritems():
            items.extend(pair)
        
        keys = {}
        for key, val in mapping.iteritems():
            hostkey = self.get_server(key)
            if hostkey in keys:
                keys[hostkey].extend([key, val])
            else:
                keys[hostkey] = [key, val]
        # keys looks like: 
        # {"server1": 
        #    [key1, val1, key2, val2],
        #  "server2": 
        #    [key3, val3, key4, val4]}
        result = True 
        for server, keys in keys.iteritems():
            tmp = self.execute_command_on_server(server, "MSET", *keys)
            result = result and tmp
        return result

    def execute_command(self, *args, **options):
        """ Picks the correct server and executes command on that server """
        
        if len(args) == 1:
            # execute command on all servers
            # assume we have to return a boolean value
            result = True
            for host, limit in self.ring:
                tmp = self.execute_command_on_server(host, *args, **options)
                result = result and tmp
            return result
        else:
            key = args[1]
            hostkey = self.get_server(key)
            return self.execute_command_on_server(hostkey, *args, **options)
        
    def execute_command_on_server(self, server, *args, **options):
        """
        All of the commands go to a single server now determined by 
        the server parameter
        """
        command_name = args[0]
        pool = self.pools[server]
        connection = pool.get_connection(command_name, **options)
        
        try:
            connection.send_command(*args)
            return self.parse_response(connection, command_name, **options) 
        except ConnectionError:
            connection.disconnect()
            connection.send_command(*args)
            return self.parse_response(connection, command_name, **options)
        finally:
            pool.release(connection)
