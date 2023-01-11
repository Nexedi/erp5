# The ingestion operation requires not only the message attribute to be present (which fluentd does automatically) but also needs the filepath attribute (in the source section of the fluentd conf set path_key filepath)
# The "filepath" contains the filepath of the log file. Because we only care about the file name, we will need to extract it, which will be used as the bucket key for the file.
# If the same "filepath" is used multiple times in different messages, the bucket data is overwritten.

try:
  l=[(c[1]["filepath"].split("/")[-1], c[1]["message"]) for c in context.unpackLazy(data_chunk, use_list=False)]
  names_message_dir = {}
  for file_name, message in l:
    try:
      names_message_dir[file_name].append(message)
    except:
      names_message_dir[file_name] = [message]

  for tag in names_message_dir:
    bucket_stream["Data Bucket Stream"].insertBucket(tag,"\n".join(names_message_dir[tag]))
except:
  context.log("The send file is missing the filepath attribute")
  pass
