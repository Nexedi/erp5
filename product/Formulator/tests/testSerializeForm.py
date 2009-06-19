# -*- coding: utf-8 -*-
import unittest

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm
from Products.Formulator.FormToXML import formToXML

from Products.Formulator.Errors import ValidationError, FormValidationError
from Testing import ZopeTestCase
ZopeTestCase.installProduct('Formulator')

class FakeRequest:
    """ a fake request for testing.
    Actually we need this only for item acces,
    and for evaluating to false always, for
    the manage_XXX methods to not try to render
    a response.
    """

    def __init__(self):
        self.dict = {}

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def get(self, key, default_value=None):
        return self.dict.get(key, default_value)

    def update(self, other_dict):
        self.dict.update(other_dict)

    def clear(self):
        self.dict.clear()

    def __nonzero__(self):
        return 0

class SerializeTestCase(unittest.TestCase):
    def test_simpleSerialize(self):
        form = ZMIForm('test', 'My test')
        xml = '''\
<?xml version="1.0" encoding="iso-8859-1" ?>

<form>
  <title></title>
  <name>tab_status_form</name>
  <action></action>
  <enctype></enctype>
  <method></method>

  <groups>
    <group>
      <title>Default</title>
      <fields>

      <field><id>message</id> <type>RawTextAreaField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <max_length></max_length>
          <width type="int">65</width>
          <external_validator></external_validator>
          <height type="int">7</height>
          <required type="int">0</required>
          <css_class></css_class>
          <default></default>
          <title>Message</title>
          <truncate type="int">0</truncate>
          <description></description>
          <extra>wrap="soft"</extra>
        </values>
        <tales>
        </tales>
      </field>
      <field><id>publish_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <css_class></css_class>
          <title>Publish time</title>
          <description></description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expiration_datetime</id> <type>DateTimeField</type>
        <values>
          <date_only type="int">0</date_only>
          <alternate_name></alternate_name>
          <input_style>list</input_style>
          <css_class></css_class>
          <hidden type="int">0</hidden>
          <input_order>dmy</input_order>
          <time_separator>:</time_separator>
          <date_separator>/</date_separator>
          <external_validator></external_validator>
          <required type="int">0</required>
          <default_now type="int">0</default_now>
          <title>Expiration time</title>
          <description>If this document should expire, set the time.</description>
        </values>
        <tales>
          <time_separator>python:form.time_punctuation</time_separator>
          <date_separator>python:form.date_punctuation</date_separator>
        </tales>
      </field>
      <field><id>expires_flag</id> <type>CheckBoxField</type>
        <values>
          <alternate_name></alternate_name>
          <hidden type="int">0</hidden>
          <css_class></css_class>
          <default type="int">0</default>
          <title>Expire flag</title>
          <description>Turn on expiration time?</description>
          <external_validator></external_validator>
          <extra></extra>
        </values>
        <tales>
        </tales>
      </field>
      </fields>
    </group>
  </groups>
</form>'''
        XMLToForm(xml, form)
        s = formToXML(form)
        f = open('output1.txt', 'w')
        f.write(s)
        f.close()
        form2 = ZMIForm('another', 'Something')
        XMLToForm(xml, form2)
        f = open('output2.txt', 'w')
        f.write(formToXML(form2))
        f.close()


    def test_escaping(self):
        """ test if the necessary elements are escaped in the XML.
        (Actually this test is very incomplete)
        """
        form = ZMIForm('test', '<EncodingTest>')
        # XXX don't test escaping of name, as needs to be javascript
        # valid anyway?
        form.name = 'name'
        form.add_group('a & b')

        form.manage_addField('string_field', '<string> Field', 'StringField')
        form.manage_addField('int_field', '<int> Field', 'IntegerField')
        form.manage_addField('float_field', '<Float> Field', 'FloatField')
        form.manage_addField('date_field', '<Date> Field', 'DateTimeField')
        form.manage_addField('list_field', '<List> Field', 'ListField')
        form.manage_addField('multi_field', '<Checkbox> Field', 'MultiCheckBoxField')

        form2 = ZMIForm('test2', 'ValueTest')

        xml = formToXML(form)
        XMLToForm(xml, form2)

        for field in form.get_fields():
            self.assert_(form2.has_field(field.getId()))
            field2 = getattr(form2, field.getId())
            # XXX test if values are the same
            self.assertEquals(field.values, field2.values)
            # test if default renderings are the same
            self.assertEquals(field.render(), field2.render())

        self.assertEquals(form.title, form2.title)
        self.assertEquals(form.name, form2.name)
        self.assertEquals(form.action, form2.action)
        self.assertEquals(form.enctype, form2.enctype)
        self.assertEquals(form.method, form2.method)

        # if we have forgotten something, this will usually remind us ;-)
        self.assertEquals(form.render(), form2.render())


    def test_messages(self):
        """ test if the error messages are exported
        """
        form = ZMIForm('test', '<EncodingTest>')
        form.manage_addField('int_field', 'int Field', 'IntegerField')
        
        form2 = ZMIForm('test2', 'ValueTest')
        request = FakeRequest()
        for message_key in form.int_field.get_error_names():
           request[message_key] = 'test message for error key <%s>' % message_key
        form.int_field.manage_messages(REQUEST=request)
        
        
        xml = formToXML(form)
        XMLToForm(xml, form2)
        # print xml

        request.clear()
        request['field_int_field'] = 'not a number'

        try:
            form.validate_all(request)
            self.fail('form should fail in validation')
        except FormValidationError, e:
            self.assertEquals(1, len(e.errors))
            text1 = e.errors[0].error_text

        try:
            form2.validate_all(request)
            self.fail('form2 should fail in validation')
        except FormValidationError, e:
            self.assertEquals(1, len(e.errors))
            text2 = e.errors[0].error_text

        self.assertEquals(text1, text2)


    def test_fieldValueTypes(self):
        """ test checking if the field values are of the proper type.
        after reading from XML some field values may not have the right type,
        if they have a special type (currently int and "list").
        Also tests if rendering and validation are the same
        between the original form and the one after one form -> xml -> form
        roundtrip.
        """

        form = ZMIForm('test', 'ValueTest')
        form.manage_addField('int_field', 'Test Integer Field', 'IntegerField')
        form.manage_addField('float_field', 'Test Float Field', 'FloatField')
        form.manage_addField('date_field', 'Test Date Field', 'DateTimeField')
        form.manage_addField('list_field', 'Test List Field', 'ListField')
        form.manage_addField('multi_field', 'Test Checkbox Field', 'MultiCheckBoxField')
        form.manage_addField('link_field', 'Test Link Field', 'LinkField')
        form.manage_addField('empty_field', 'Test Empty Field', 'StringField')
        int_field   = getattr(form, 'int_field')
        float_field = getattr(form, 'float_field')
        date_field  = getattr(form, 'date_field')
        list_field  = getattr(form, 'list_field')
        multi_field = getattr(form, 'multi_field')
        link_field = getattr(form, 'link_field')
        empty_field = getattr(form, 'empty_field')

        # XXX editing fields by messing with a fake request
        # -- any better way to do this?
        default_values = {'field_title': 'Test Title',
                          'field_display_width': '92',
                          'field_required':'checked',
                          'field_enabled':'checked',
                          }
        try:
            request = FakeRequest()
            for key, sub_field in int_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'42',
                             'field_enabled':'checked'})
            int_field.manage_edit(REQUEST=request)

            request.clear()
            for key, sub_field in float_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'1.7',
                             'field_input_style':'-1234.5'})
            float_field.manage_edit(REQUEST=request)

            # XXX cannot test "defaults to now", as this may fail randomly
            request.clear()
            for key, sub_field in date_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_input_style': 'list',
                             'field_input_order': 'mdy',
                             'field_date_only': '',
                             'field_css_class': 'test_css',
                             'field_time_separator': '$',
                             'subfield_field_default_year': '',
                             'subfield_field_default_month': '',
                             'subfield_field_default_day': '',
                             'subfield_field_default_hour': '',
                             'subfield_field_default_minute': '',
                             'subfield_field_start_datetime_year': '',
                             'subfield_field_start_datetime_month': '',
                             'subfield_field_start_datetime_day': '',
                             'subfield_field_start_datetime_hour': '',
                             'subfield_field_start_datetime_minute': '',
                             'subfield_field_end_datetime_year': '',
                             'subfield_field_end_datetime_month': '',
                             'subfield_field_end_datetime_day': '',
                             'subfield_field_end_datetime_hour': '',
                             'subfield_field_end_datetime_minute': '',
                          })
            date_field.manage_edit(REQUEST=request)

            request.clear()
            for key, sub_field in list_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'foo',
                             'field_size':'1',
                             'field_items':'Foo | foo\n Bar | bar'})
            list_field.manage_edit(REQUEST=request)

            request.clear()
            for key, sub_field in multi_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'foo',
                             'field_size':'3',
                             'field_items':'Foo | foo\n Bar | bar\nBaz | baz',
                             'field_orientation':'horizontal',
                             'field_view_separator':'<br />\n',
                             })
            multi_field.manage_edit(REQUEST=request)

            request.clear()
            for key, sub_field in link_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'http://www.absurd.org',
                             'field_required':'1',
                             'field_check_timeout':'5.0',
                             'field_link_type':'external',
                             })
            link_field.manage_edit(REQUEST=request)

            request.clear()
            for key, sub_field in empty_field.form.fields.iteritems():
              request['field_%s' % key] = sub_field.render_pdf()
            request.update(default_values)
            request.update( {'field_default':'None',
                             'field_required':'',
                             })
            empty_field.manage_edit(REQUEST=request)

        except ValidationError, e:
            self.fail('error when editing field %s; error message: %s' %
                       (e.field_id, e.error_text) )

        form2 = ZMIForm('test2', 'ValueTest')

        xml = formToXML(form)
        XMLToForm(xml, form2)

        for field in form.get_fields():
            self.assert_(form2.has_field(field.getId()))
            field2 = getattr(form2, field.getId())
            # XXX test if values are the same
            self.assertEquals(field.values, field2.values)
            # test if default renderings are the same
            self.assertEquals(field.render(), field2.render())

        # brute force compare ...
        self.assertEquals(form.render(), form2.render())
        request.clear()
        request['field_int_field'] = '42'
        request['field_float_field'] = '2.71828'
        request['subfield_field_date_field_month'] = '11'
        request['subfield_field_date_field_day'] = '11'
        request['subfield_field_date_field_year'] = '2011'
        request['subfield_field_date_field_hour'] = '09'
        request['subfield_field_date_field_minute'] = '59'
        request['field_list_field'] = 'bar'
        request['field_multi_field'] = ['bar', 'baz']
        request['field_link_field'] = 'http://www.zope.org'
        request['default_field_multi_field'] = ''
        request['field_empty_field'] = ''
        try:
            result1 = form.validate_all(request)
        except FormValidationError, e:
            # XXX only render first error ...
            self.fail('error when editing form1, field %s; error message: %s' %
                       (e.errors[0].field_id, e.errors[0].error_text) )

        try:
            result2 = form2.validate_all(request)
        except FormValidationError, e:
            # XXX only render first error ...
            self.fail('error when editing form1, field %s; error message: %s' %
                       (e.errors[0].field_id, e.errors[0].error_text) )
        self.assertEquals(result1, result2)
        self.assertEquals(42, result2['int_field'])
        self.assertEquals(2.71828, result2['float_field'])

	# check link field timeout value
	self.assertEquals(link_field.get_value('check_timeout'),
                          form2.link_field.get_value('check_timeout'))

        # XXX not tested: equal form validation failure on invalid input
        
        

    def test_emptyGroup(self):
        """ test bugfix: empty groups are allowed in the XMLForm """
        form = ZMIForm('test', 'GroupTest')
        form.add_group('empty')
        
        form2 = ZMIForm('test2', 'GroupTestCopy')
        
        xml = formToXML(form)
        XMLToForm(xml, form2)
        # print xml

        # XXX actually the empty group is not rendered anyway, but
        # if we get here, we are behind the bug anyway ...
        self.assertEquals(form.render(), form2.render())

        self.assertEquals(form.get_groups(), form2.get_groups())
    
        
def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(SerializeTestCase, 'test'))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
