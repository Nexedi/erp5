##USER = 'USER'
##PORTAL = 'PORTAL'
##GLOBAL = 'GLOBAL'
##HOST = 'HOST'
##THREAD = 'THREAD'
##
##CACHE_SCOPES = (USER, PORTAL,GLOBAL, HOST, THREAD,)
##DEFAULT_CACHE_SCOPE = USER
##
##DEFAULT_CACHE_STRATEGY = ('quick_cache', 'persistent_cache', )
##
##
#### TODO: DistributedRamCache and SQLCache must be able to read their 
#### configuration properties when CachingMethod is initialized
#### Sepcifying in config.py isn't the best way?!
##
##CACHE_PLUGINS_MAP = {## Local RAM based cache
##                     'quick_cache': {'className': 'RamCache',
##                                      'fieldName': 'ram_cache',
##                                      'params': {},
##                                    },
##
##                     ## Memcached
##                     'shared_cache':{'className': 'DistributedRamCache',
##                                     'fieldName': 'distributed_ram_cache',
##                                     'params': {'servers': '127.0.0.1:11211',
##                                                'debugLevel': 7,
##                                                }
##                                    },
##
##                     ## MySQL cache              
##                     'persistent_cache':{'className': 'SQLCache',
##                                         'fieldName': 'sql_cache',
##                                         'params': {'server': 'localhost',
##                                                    'user': 'zope',
##                                                    'passwd': 'zope_pass',
##                                                    'db': 'cache',
##                                                    'cache_table_name': 'cache',
##                                                   }
##                                        },
##                      
##                     ## Dummy (no cache)
##                     'dummy_cache': {'className': 'DummyCache',
##                                      'fieldName': 'dummy_cache',
##                                      'params': {},
##                                    },
##                    }
