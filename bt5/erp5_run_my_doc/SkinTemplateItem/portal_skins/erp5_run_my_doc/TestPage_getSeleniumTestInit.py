request = context.REQUEST

url = request.get('url', None)
if url is not None:
  html_init = """<tr>
          <td>store</td>
          <td>%s</td>
          <td>base_url</td>
        </tr>""" % url
else:
  html_init = """<span metal:use-macro="container/Zuite_CommonTemplate/macros/init" style="display: none;">init</span>"""

user = request.get('user')
if user:
  html_init += """
        <tr>
          <td>store</td>
          <td>{user}</td>
          <td>base_user</td>
        </tr>
        <tr>
          <td>store</td>
          <td>{password}</td>
          <td>base_password</td>
        </tr>""".format(user=user, password=request['password'])
else:
  html_init += """
        <tr>
          <td>storeEval</td>
          <td>selenium.getCookieByName("manager_username")</td>
          <td>base_user</td>
        </tr>
        <tr>
          <td>storeEval</td>
          <td>selenium.getCookieByName("manager_password")</td>
          <td>base_password</td>
        </tr>"""

return html_init
