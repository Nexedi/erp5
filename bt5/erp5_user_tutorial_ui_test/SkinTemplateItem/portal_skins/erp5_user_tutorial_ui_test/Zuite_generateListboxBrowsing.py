selenium_code = \
"""\
<tr>
  <td>clickAndWait</td>
  <td>//button[@name="Folder_show:method"]</td>
  <td></td>
</tr>
"""

for selection in listbox_selection:
  selenium_code += \
"""\
<tr>
  <td>type</td>
  <td>//tr[@class='listbox-search-line']/th[@class="listbox-table-filter-cell"]/input[@name='listbox_%s']</td>
  <td>%s</td>
</tr>
""" % (selection[0], selection[1])


selenium_code += \
"""\
<tr>
  <td>clickAndWait</td>
  <td>//input[@name=\"Base_doSelect:method\"]</td>
  <td></td>
</tr>
"""

if enter_object:
  selenium_code += \
"""\
<tr>
  <td>clickAndWait</td>
  <td>link=%s</td>
  <td></td>
</tr>
""" % listbox_selection[0][1]


return selenium_code
