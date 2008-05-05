msg = container.my_mt.as_message(
    mfrom='from@example.com',
    mto='to1@example.com',
    subject='Your requested file',
    boundary='111' # for testing only, so we get a consistent boundary
    )
msg.add_file(container['myfile.bin'])
msg.send()
return 'Mail Sent!'
