## Script (Python) "update_computer_product"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=Update a Computer Product
##
if context.meta_type == 'MMM Computer Product' or context.meta_type == 'Storever Computer Product':
    context.editProduct(title=REQUEST['prod_name']
                        , description=REQUEST['description']
                        , price=REQUEST['price']
                        , isCredit=REQUEST['isCredit']
                        , credits = REQUEST['credits']
                        , category=REQUEST['prod_category']
                        , delivery_days=REQUEST['delivery_days']
                        , product_path = REQUEST['product_path']
			, text= REQUEST['text'])
    # Update Processor
    l = len(context.getProcessorSizes())
    for i in context.getProcessorSizes():
        context.deleteProcessorPrice(i)
    for i in range(1,l+1):
        if REQUEST['procsize_%s' % i] != '':
            context.setProcessorPrice(str(REQUEST['procsize_%s' % i]),float(REQUEST['procprice_%s' % i]))
    if REQUEST['procsize_new'] != '':
        context.setProcessorPrice(str(REQUEST['procsize_new']),float(REQUEST['procprice_new']))
    # Update Memory
    l = len(context.getMemorySizes())
    for i in context.getMemorySizes():
        context.deleteMemoryPrice(i)
    for i in range(1,l+1):
        if REQUEST['memsize_%s' % i] != '':
            context.setMemoryPrice(str(REQUEST['memsize_%s' % i]),float(REQUEST['memprice_%s' % i]))
    if REQUEST['memsize_new'] != '':
        context.setMemoryPrice(str(REQUEST['memsize_new']),float(REQUEST['memprice_new']))
    # Update Disk
    l = len(context.getDiskSizes())
    for i in context.getDiskSizes():
        context.deleteDiskPrice(i)
    for i in range(1,l+1):
        if REQUEST['disksize_%s' % i] != '':
            context.setDiskPrice(str(REQUEST['disksize_%s' % i]),float(REQUEST['diskprice_%s' % i]))
    if REQUEST['disksize_new'] != '':
        context.setDiskPrice(str(REQUEST['disksize_new']),float(REQUEST['diskprice_new']))
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
        memberfolder = context.portal_membership.getHomeFolder()
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
        member_folder = context.portal_membership.getHomeFolder()
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

context.REQUEST.RESPONSE.redirect(context.local_absolute_url() + '/computerproduct_edit_form?portal_status_message=' + status_msg)
