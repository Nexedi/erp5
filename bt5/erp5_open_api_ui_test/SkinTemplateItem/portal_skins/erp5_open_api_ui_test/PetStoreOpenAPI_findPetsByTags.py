"""Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.

GET /pet/findByTags
"""

pets = []
for i, tag in enumerate(tags):
  pets.append({
    'id': i,
    'name': 'doggie',
    'category': {
      'id': 1,
      'name': 'Dogs'
    },
    'photoUrls': [],
    'tags': [
      {
        'id': i,
        'name': tag
      }
    ],
    'status': 'available'
  })

return pets
