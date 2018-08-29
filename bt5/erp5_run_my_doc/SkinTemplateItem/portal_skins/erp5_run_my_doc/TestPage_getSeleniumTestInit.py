request = context.REQUEST

url = request.get('url', None)
if url is not None:
  html_init = """<tr>
          <td>store</td>
          <td>%s</td>
          <td>base_url</td>
        </tr>
""" % url
else:
  html_init = """<span metal:use-macro="container/Zuite_CommonTemplate/macros/init" style="display: none;">init</span>"""

html_init += """        <tr>
          <td>store</td>
          <td>%s</td>
          <td>base_user</td>
         </tr>
""" % request.get('user', manager_username)

html_init += """        <tr>
          <td>store</td>
          <td>%s</td>
          <td>base_password</td>
         </tr>""" % request.get('password', manager_password)

return html_init
