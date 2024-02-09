from json import dumps

request = context.REQUEST

# render real gadget content as HTML
html = context.ERP5Site_viewRssGadget()
box_relative_url = request.get('box_relative_url', None)
box = context.restrictedTraverse(box_relative_url)

box_dom_id = box.getRelativeUrl().replace('/', '_')
gadget_title_dom_id = '%s_gadget_title' %box_dom_id

# return some JavaScript which will update respective page
gadget_title = request.get('rss_gadget_title', box.getSpecialiseValue().getTitle())
gadget_title = gadget_title[:40]
javascript = '$("#%s").html("%s");' %(gadget_title_dom_id, gadget_title)

request.RESPONSE.setHeader("Content-Type", "application/json;; charset=utf-8")
result =  {"body": html,
          "javascript": javascript}
return dumps(result)
