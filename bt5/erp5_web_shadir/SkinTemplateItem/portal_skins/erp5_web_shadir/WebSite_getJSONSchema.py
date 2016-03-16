return {
   'type': 'array',
   'items': [
      {'type': 'object',
       'properties':{
          'file':{
             'type': 'string',
             'required': True,
          },
          'urlmd5': {
             'type': 'string',
             'required': True,
          },
          'sha512': {
             'type': 'string',
             'required': True,
          },
          'creation_date': {
             'type': 'string',
             'required': False,
          },
          'expiration_date': {
             'type': 'string',
             'required': False,
          },
          'distribution': {
             'type': 'string',
             'required': False,
          },
          'architecture': {
             'type': 'string',
             'required': False,
          },
       }
     },
     {'type': 'string',
      'blank': True},
   ]
}
