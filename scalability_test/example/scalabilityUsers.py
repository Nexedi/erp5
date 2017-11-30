# Specify user login/password used to run the tests.
# <password> and <user_quantity> will be automatically replaced by testnode for each configuration

user_tuple = tuple([('scalability_user_%i' % x, "<password>") for x in range(0, <user_quantity>)])