import XMLObjects
from Products.Formulator.TALESField import TALESMethod
from Products.Formulator.MethodField import Method

def XMLToForm(s, form, override_encoding=None):
    """Takes an xml string and changes formulator form accordingly.
    Heavily inspired by code from Nikolay Kim.

    If override_encoding is set, form data is read assuming given
    encoding instead of the one in the XML data itself. The form will
    have to be modified afterwards to this stored_encoding itself.
    """
    top = XMLObjects.XMLToObjectsFromString(s)
    # wipe out groups
    form.groups = {'Default':[]}
    form.group_list = ['Default']

    if override_encoding is None:
        try:
            unicode_mode = top.first.form.first.unicode_mode.text
        except AttributeError:
            unicode_mode = 'false'
        # retrieve encoding information from XML
        if unicode_mode == 'true':
            # just use unicode strings being read in
            encoding = None
        else:
            # store strings as specified encoding
            try:
                encoding = top.first.form.first.stored_encoding.text
            except AttributeError:
                encoding = 'ISO-8859-1'
    else:
        if override_encoding == 'unicode':
            encoding = None
        else:
            encoding = override_encoding
        
    #  get the settings
    settings = [field.id for field in form.settings_form.get_fields()]    
    for setting in settings:
        value = getattr(top.first.form.first, setting, None)
        if value is None:
            continue
        if setting == 'unicode_mode':
            v = value.text == 'true'
        elif setting == 'row_length':
            v = int(value.text)
        else:
            v = encode(value.text, encoding)
        setattr(form, setting, v) 

    # create groups
    has_default = 0
    for group in top.first.form.first.groups.elements.group:
        # get group title and create group
        group_title = encode(group.first.title.text, encoding)
        if group_title == 'Default':
            has_default = 1
        form.add_group(group_title)
        # create fields in group
        if not hasattr(group.first.fields.elements, 'field'):
            # empty <fields> element
            continue
        for entry in group.first.fields.elements.field:
            id = str(encode(entry.first.id.text, encoding))
            meta_type = encode(entry.first.type.text, encoding)
            try:
                form._delObject(id)
            except (KeyError, AttributeError):
                pass
            form.manage_addField(id, '', meta_type)
            field = form._getOb(id)
            if group_title != 'Default':
                form.move_field_group([id], 'Default', group_title)
            # set values
            values = entry.first.values
            for name in values.getElementNames():
                value = getattr(values.first, name)
                if value.attributes.get('type') == 'float':
                    field.values[name] = float(value.text)
                elif value.attributes.get('type') == 'int':
                    field.values[name] = int(value.text)
                elif value.attributes.get('type') == 'method': # XXX Patch
                    field.values[name] = Method(value.text) # XXX Patch
                elif value.attributes.get('type') == 'list':
                    # XXX bare eval here (this may be a security leak ?)
                    field.values[name] = eval(
                        encode(value.text, encoding))
                else:
                    field.values[name] = encode(value.text, encoding)

            # special hack for the DateTimeField
            if field.meta_type=='DateTimeField':
                field.on_value_input_style_changed(
                    field.get_value('input_style'))

            # set tales
            tales = entry.first.tales
            for name in tales.getElementNames():
                field.tales[name] = TALESMethod(
                    encode(getattr(tales.first, name).text, encoding))

            # set messages
            if hasattr(entry.first, 'messages'):
                messages = entry.first.messages
                entries = getattr(messages.elements, 'message', [])
                for entry in entries:
                    name = entry.attributes.get('name')
                    text = encode(entry.text, encoding)
                    field.message_values[name] = text

            # for persistence machinery
            field.values = field.values
            field.tales = field.tales
            field.message_values = field.message_values
        
    # delete default group
    if not has_default:
        form.move_group_down('Default')
        form.remove_group('Default')
    
def encode(text, encoding):
    if encoding is None:
        return text
    else:
        return text.encode(encoding)
