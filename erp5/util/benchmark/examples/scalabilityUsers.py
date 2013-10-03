# Specify user login/password used to run the tests. Note that there must be
# the same number of users specified here *and* on the script command-line.
user_tuple = tuple([('scalability_user_%i' % x, 'insecure') for x in range(0, 1000)])
