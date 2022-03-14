from Products.ERP5Type.Utils import md5
password, = sci['kwargs']['workflow_method_args']

sci['object'].setEncodedPassword(md5(password).hexdigest(), format='palo_md5')
