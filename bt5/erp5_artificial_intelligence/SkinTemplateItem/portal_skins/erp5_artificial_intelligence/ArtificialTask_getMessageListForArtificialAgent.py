artificial_task = context
message_list = []
for post in artificial_task.ArtificialTask_getCommentPostList():
  message_list.append({
    "role": "assistant" if post["author_url"] == artificial_agent_url else "user",
    "content": post["text"],
  })
return message_list
