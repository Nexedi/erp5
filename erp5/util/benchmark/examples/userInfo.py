# Specify user login/password used to run the tests. Note that there must be
# the same number of users specified here *and* on the script command-line.
user_tuple = (('zope', 'zope'),)

# A more complex example setting the source IP address as well, assuming the
# users and network alias interfaces (not necessary with SlapOS though) have
# been created beforehand
#user_tuple = tuple((('zope%d' % i, 'zope', '192.168.168.%d' % (i + 1))
#                    for i in range(30)))
