container.my_mt(
    mto='user@example.com',
    subject=container.my_mt.subject % container.absolute_url()
    )

return 'Mail Sent!'
