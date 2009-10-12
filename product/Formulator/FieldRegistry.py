import os
import OFS
from App.ImageFile import ImageFile
from FieldHelpTopic import FieldHelpTopic

class FieldRegistry:
    """A registry of fields, maintaining a dictionary with
    the meta_type of the field classes as key and the field class as
    values. Updates the Form as necessary as well.
    """
    def __init__(self):
        """Initializer of FieldRegistry.
        """
        self._fields = {}

    def get_field_class(self, fieldname):
        """Get a certain field class by its name (meta_type)
        fieldname -- the name of the field to get from the registry
        """
        return self._fields[fieldname]

    def get_field_classes(self):
        """Return all fields.
        """
        return self._fields
    
    def registerField(self, field_class, icon=None):
        """Register field with Formulator.
        field_class -- the class of the field to be registered
        icon        -- optional filename of the icon
        """
        # put it in registry dictionary
        self._fields[field_class.meta_type] = field_class
        # set up dummy fields in field's form
        initializeFieldForm(field_class)
        # set up the icon if a filename is supplied
        if icon:
            setupIcon(field_class, icon, 'Formulator')

    def registerFieldHelp(self, *args, **kw):
        """XXX: this is a quick fix to avoid bloating the ZODB.
           Proper fix should only add FieldHelp when it's missing.
        """
        pass

    def initializeFields(self):
        """Initialize all field classes in field forms to use actual field
        objects so we can finally eat our own dogfood.
        """
        # for each field, realize fields in form
        # this is finally possible as all field classes are now
        # fully defined.
        for field_class in self._fields.values():
            field_class.form._realize_fields()
            field_class.override_form._realize_fields()
            field_class.tales_form._realize_fields()
            
# initialize registry as a singleton
FieldRegistry = FieldRegistry()
        
def initializeFieldForm(field_class):
    """Initialize the properties (fields and values) on a particular
    field class. Also add the tales and override methods.
    """
    from Form import BasicForm
    from DummyField import fields
    
    form = BasicForm()
    override_form = BasicForm()
    tales_form = BasicForm()
    for field in getPropertyFields(field_class.widget):
        form.add_field(field, "widget")
        tales_field = fields.TALESField(field.id,
                                        title=field.get_value('title'),
                                        description="",
                                        default="",
                                        display_width=40,
                                        required=0)
        tales_form.add_field(tales_field, "widget")
        
        method_field = fields.MethodField(field.id,
                                          title=field.get_value("title"),
                                          description="",
                                          default="",
                                          required=0)
        override_form.add_field(method_field, "widget")
        
    for field in getPropertyFields(field_class.validator): 
        form.add_field(field, "validator")
        tales_field = fields.TALESField(field.id,
                                        title=field.get_value('title'),
                                        description="",
                                        default="",
                                        display_with=40,
                                        required=0)
        tales_form.add_field(tales_field, "validator")
        
        method_field = fields.MethodField(field.id,
                                          title=field.get_value("title"),
                                          description="",
                                          default="",
                                          required=0)
        override_form.add_field(method_field, "validator")
        
    field_class.form = form         
    field_class.override_form = override_form
    field_class.tales_form = tales_form
    
def getPropertyFields(obj):
    """Get property fields from a particular widget/validator.
    """
    fields = []
    for property_name in obj.property_names:
        fields.append(getattr(obj, property_name))
    return fields

def setupIcon(klass, icon, repository):
    """Load icon into Zope image object and put it in Zope's
    repository for use by the ZMI, for a particular class.
    klass -- the class of the field we're adding
    icon  -- the icon
    """
    # set up misc_ respository if not existing yet
    if not hasattr(OFS.misc_.misc_, repository):
        setattr(OFS.misc_.misc_, 
                repository, 
                OFS.misc_.Misc_(repository, {}))
        
    # get name of icon in the misc_ directory
    icon_name = os.path.split(icon)[1]
        
    # set up image object from icon file
    icon_image = ImageFile(icon, globals())
    icon_image.__roles__ = None

    # put icon image object in misc_/Formulator/
    getattr(OFS.misc_.misc_, repository)[icon_name] = icon_image

    # set icon attribute in field_class to point to this image obj
    setattr(klass, 'icon', 'misc_/%s/%s' %
            (repository, icon_name))     

