# vredis

A V-Bucket aware redis client for Python.
Allows distribution of Redis data across multiple servers.

## Prerequisites

vredis requires redis-py from Andy McCurdy to be installed first: https://github.com/andymccurdy/redis-py

    $ sudo pip install redis

## Installation

    $ sudo pip install vredis

From source:

    $ sudo python setup.py install

## Getting Started

    >>> import vredis
    >>> r = vredis.VRedis(hosts=[('localhost', 6379, 128), ('localhost', 6379, 255)])
    >>> r.set('foo', 'bar')
    True
    >>> r.get('foo')
    'bar'
    
hosts parameter is a list of tuples, one for each server. Each tuple specifies hostname, port, and ending bucket in the hash ring (out of 255).

The example above has 2 identical hosts using port 6379, first one gets hashes 0..128, second one gets 129..255. 

## Current stage

dbsize, keys, flushall, set, get, mset, and mget have been implemented and tested in VRedis

## TODO

implement and test all the other commands from http://redis.io/commands
