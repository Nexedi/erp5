## Script (Python) "update_computer_product"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=Update a Computer Product
##
if context.meta_type == 'Storever Simple Product':
    context.editProduct(title=REQUEST['prod_name']
                        , description=REQUEST['description']
                        , price=REQUEST['price']
                        , isCredit=REQUEST['isCredit']
                        , category=REQUEST['prod_category']
                        , delivery_days=REQUEST['delivery_days']
                        , product_path = REQUEST['product_path']
			, text= REQUEST['text'])
    # Update Options
    l = len(context.getOptions())
    for i in context.getOptions():
        context.deleteOptionPrice(i)
    for i in range(1,l+1):
        if REQUEST['option_%s' % i] != '':
            context.setOptionPrice(str(REQUEST['option_%s' % i]),float(REQUEST['optionprice_%s' % i]))
    if REQUEST['option_new'] != '':
        context.setOptionPrice(str(REQUEST['option_new']),float(REQUEST['optionprice_new']))
    # Update standard product fields
    status_msg = 'Product+updated'
    if REQUEST['thumbnail'] != '':
        t_id = context.id + '_thumbnail'
        user_obj = context.getMemberObj()
        username = user_obj.getUserName()
        memberfolder = context.portal_membership.getHomeFolder(username)
        t_obj = None
        for item in memberfolder.objectValues(('Portal Image','Base18 Image')):
            if item.getId() == t_id:
                t_obj = memberfolder.restrictedTraverse(item.getId())

        if t_obj is None:
            memberfolder.invokeFactory(id=t_id, type_name='Image')
            t_obj = memberfolder.restrictedTraverse(t_id)

        t_obj.edit(precondition='', file=REQUEST['thumbnail'])
        context.editThumbnail(t_obj.absolute_url(relative=1))
        status_msg = status_msg + ',+Thumbnail+updated'

    if REQUEST['image'] != '':
        i_id = context.id + '_image'
        user_obj = context.getMemberObj()
        username = user_obj.getUserName()
        member_folder = context.portal_membership.getHomeFolder(username)
        i_obj = None
        for item in member_folder.objectValues(('Portal Image','Base18 Image')):
            if item.getId() == i_id:
                i_obj = member_folder.restrictedTraverse(item.getId())

        if i_obj is None:
            member_folder.invokeFactory(id=i_id, type_name='Image')
            i_obj = member_folder.restrictedTraverse(i_id)

        i_obj.edit(precondition='', file=REQUEST['image'])
        context.editImage(i_obj.absolute_url(relative=1))
        status_msg = status_msg + ',+Large+image+updated'

else:
    status_msg = 'Update+script+called+in+wrong+context'

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/simpleproduct_edit_form?portal_status_message=' + status_msg)
