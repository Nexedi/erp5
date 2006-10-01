
class ExternalDocument:
  """
  """
  _properties = (
        {   'id'          : 'status_message',
            'description' : 'message about status',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'option_recursively',
            'description' : 'do we want recursive spidering (meaningless in some classes)',
            'type'        : 'int',
            'mode'        : 'w'},
        {   'id'          : 'recursion_depth',
            'description' : 'how deep should recursive spidering be (0 - no recursion) (meaningless in some classes)',
            'type'        : 'int',
            'default'     : 5,
            'mode'        : 'w'},
        )

