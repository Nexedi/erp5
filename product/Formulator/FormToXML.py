from StringIO import StringIO
from cgi import escape
import types

#def write(s):
#    if type(s) == type(u''):
#        print "Unicode:", repr(s)
    
def formToXML(form, prologue=1):
    """Takes a formulator form and serializes it to an XML representation.
    """
    f = StringIO()
    write = f.write

    if prologue:
        write('<?xml version="1.0"?>\n\n')
    write('<form>\n')
    # export form settings
    for field in form.settings_form.get_fields(include_disabled=1):
        id = field.id
        value = getattr(form, id)
        if id == 'title':
            value = escape(value)
        if id == 'unicode_mode':
            if value:
                value = 'true'
            else:
                value = 'false'
        write('  <%s>%s</%s>\n' % (id, value, id))
    # export form groups
    write('  <groups>\n')
    for group in form.get_groups(include_empty=1):
        write('    <group>\n')
        write('      <title>%s</title>\n' % escape(group))
        write('      <fields>\n\n')
        for field in form.get_fields_in_group(group, include_disabled=1):
            write('      <field><id>%s</id> <type>%s</type>\n' % (field.id, field.meta_type))
            write('        <values>\n')
            items = field.values.items()
            items.sort()
            for key, value in items:
                if value is None:
                    continue
                if value==True: # XXX Patch
                    value = 1 # XXX Patch
                if value==False: # XXX Patch
                    value = 0 # XXX Patch
                if callable(value): # XXX Patch
                    write('          <%s type="method">%s</%s>\n' % # XXX Patch
                        (key, escape(str(value.method_name)), key)) # XXX Patch
                elif type(value) == type(1.1):
                    write('          <%s type="float">%s</%s>\n' % (key, escape(str(value)), key))
                elif type(value) == type(1):
                    write('          <%s type="int">%s</%s>\n' % (key, escape(str(value)), key))
                elif type(value) == type([]):
                    write('          <%s type="list">%s</%s>\n' % (key, escape(str(value)), key))
                else:
                    if type(value) not in (types.StringType, types.UnicodeType):
                        value = str(value)
                    write('          <%s>%s</%s>\n' % (key, escape(value), key))
            write('        </values>\n')

            write('        <tales>\n')
            items = field.tales.items()
            items.sort()
            for key, value in items:
                if value:
                    write('          <%s>%s</%s>\n' % (key, escape(str(value._text)), key))
            write('        </tales>\n')

            write('        <messages>\n')
            for message_key in field.get_error_names():
                write('          <message name="%s">%s</message>\n' %
                      (escape(message_key), escape(field.get_error_message(message_key))))
            write('        </messages>\n')
            write('      </field>\n')
        write('      </fields>\n')
        write('    </group>\n')
    write('  </groups>\n')
    write('</form>')

    if form.unicode_mode:
        return f.getvalue().encode('UTF-8')
    else:
        return unicode(f.getvalue(), form.stored_encoding).encode('UTF-8')
