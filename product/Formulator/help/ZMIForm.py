
class ZMIForm:
    """Form used from Zope Management Interface. Inherits from
    ObjectManager to present folderish view.
    """

    __extends__ = ('Formulator.Form.Form',
                   'OFSP.ObjectManager.ObjectManager',
                   'OFSP.ObjectManagerItem.ObjectManagerItem')


    def manage_addField(id, title, fieldname, REQUEST=None):
        """
        Add a new field with 'id' and 'title' of field type
        'fieldname' to this ZMIForm. 'REQUEST' is optional.  Note that
        it's better to use BasicForm and 'add_field' if you want to
        use Formulator Forms outside the Zope Management Interface.
        
        Permission -- 'Change Formulator Forms'
        """

        
        
    
