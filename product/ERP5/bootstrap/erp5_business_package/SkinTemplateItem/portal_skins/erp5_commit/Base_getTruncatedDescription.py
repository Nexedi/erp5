object_truncated_description_length = 72 # as in Fortran70 (it must be greeter than 3)

object_description = context.getDescription('')
word_list = object_description.split()

object_flat_description = ' '.join(word_list)
if len(object_flat_description) <= object_truncated_description_length:
  return object_flat_description

# object_truncated_description = object_flat_description[:object_truncated_description_length - 3] + '...'
object_truncated_description = ''
for word in word_list:
  if len(object_truncated_description) + len(word) + 4 <= object_truncated_description_length:
    object_truncated_description += word + ' '
  else:
    last_word = word
    break
truncated_last_word = last_word[:object_truncated_description_length - len(object_truncated_description) - 3]
if truncated_last_word != last_word:
  object_truncated_description += truncated_last_word
object_truncated_description += '...'
return object_truncated_description
