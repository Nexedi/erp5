from Globals import DTMLFile
from HelpSys import HelpTopic

class FieldHelpTopic(HelpTopic.HelpTopic):
    """A special help topic for fields.
    """
    meta_type = 'Help Topic'
    
    def __init__(self, id, title, field_class,
                 permissions=None, categories=None):
        self.id = id
        self.title = title
        self.field_class = field_class
                                              
        if permissions is not None:
            self.permissions = permissions
        if categories is not None:
            self.categories = categories
            
    index_html = DTMLFile('dtml/FieldHelpTopic', globals())
    
    def SearchableText(self):
        """Full text of the Help Topic, for indexing purposes."""
        return "" # return self.index_html()

    def get_groups(self):
        """Get form groups of this field.
        """
        return self.field_class.form.get_groups()

    def get_fields_in_group(self, group):
        """Get the fields in the group.
        """
        return self.field_class.form.get_fields_in_group(group)
    
