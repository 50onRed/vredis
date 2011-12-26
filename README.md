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

## Current stage

set, get, mset, and mget have been implemented and tested in VRedis

## TODO

implement and test all the other commands from http://redis.io/commands
