REQUEST = context.REQUEST
return context.portal_password.changeUserPassword(password=REQUEST['password'],
                                                                    password_confirm=REQUEST['password_confirm'],
                                                                    password_key=REQUEST['password_key'],
                                                                    user_login=REQUEST.get('user_login', None),
                                                                    REQUEST=REQUEST)
