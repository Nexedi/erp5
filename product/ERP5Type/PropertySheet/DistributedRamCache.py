class DistributedRamCache:
  """
  """

  _properties = (        
        {'id'          : 'server',
         'description' : 'Memcached server address( you can specify multiple servers by separating them with ;)',
         'type'        : 'string',
         'default'     : '127.0.0.1:11211',
        },
        )

