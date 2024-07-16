# -*- coding: utf-8 -*-
import unittest
from Products.Formulator import Validator
from Products.Formulator.StandardFields import DateTimeField
from Testing import ZopeTestCase
ZopeTestCase.installProduct('Formulator')

class TestField:
    def __init__(self, id, **kw):
        self.id = id
        self.kw = kw

    def get_value(self, name):
        # XXX hack
        return self.kw.get(name, 0)

    def get_error_message(self, key):
        return "nothing"

    def get_form_encoding(self):
        # XXX fake ... what if installed python does not support utf-8?
        return "utf-8"

    def has_value(self, id):
        return id in self.kw

class ValidatorTestCase(unittest.TestCase):
    def assertValidatorRaises(self, exception, error_key, f, *args, **kw):
        try:
            f(*args, **kw)
        except exception as e:
            if hasattr(e, 'error_key') and e.error_key != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)

class StringValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.StringValidatorInstance

    def tearDown(self):
        pass

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : 'foo'})
        self.assertEqual('foo', result)

    def test_htmlquotes(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : '<html>'})
        self.assertEqual('<html>', result)

    def test_encoding(self):
        utf8_bytes = b'M\303\274ller' # this is a M&uuml;ller
        unicode_string = utf8_bytes.decode('utf-8')
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=1),
            'f', {'f' : utf8_bytes})
        self.assertEqual(unicode_string, result)

    def test_strip_whitespace(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : ' foo  '})
        self.assertEqual('foo', result)

    def test_error_too_long(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=10, truncate=0, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})

    def test_error_truncate(self):
        result = self.v.validate(
            TestField('f', max_length=10, truncate=1, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})
        self.assertEqual('this is way too long'[:10], result)

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Exception, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {})

    def test_whitespace_preserve(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f' : ' '})
        self.assertEqual(' ', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=0),
            'f', {'f' : ' '})
        self.assertEqual('', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f' : ' foo '})
        self.assertEqual(' foo ', result)

class EmailValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.EmailValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com'})
        self.assertEqual('foo@bar.com', result)
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'm.faassen@vet.uu.nl'})
        self.assertEqual('m.faassen@vet.uu.nl', result)

    def test_error_not_email(self):
        # a few wrong email addresses should raise error
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com.'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '@bar.com'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})

# skip PatternValidator for now

class BooleanValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.BooleanValidatorInstance

    def tearDown(self):
        pass

    def test_basic(self):
        result = self.v.validate(
            TestField('f'),
            'f', {'f': ''})
        self.assertEqual(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 1})
        self.assertEqual(1, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 0})
        self.assertEqual(0, result)
        result = self.v.validate(
            TestField('f', required=1),
            'f', {'f': 1})
        self.assertEqual(1, result)
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', required=1),
            'f', {'f': 0})

class IntegerValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.IntegerValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '15'})
        self.assertEqual(15, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '0'})
        self.assertEqual(0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '-1'})
        self.assertEqual(-1, result)

    def test_no_entry(self):
        # result should be empty string if nothing entered
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': ''})
        self.assertEqual("", result)

    def test_ranges(self):
        # first check whether everything that should be in range is
        # in range
        for i in range(0, 100):
            result = self.v.validate(
                TestField('f', max_length=0, truncate=0, required=1,
                          start=0, end=100),
                'f', {'f': str(i)})
            self.assertEqual(i, result)
        # now check out of range errors
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '100'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '200'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '-10'})
        # check some weird ranges
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=10, end=10),
            'f', {'f': '10'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=0),
            'f', {'f': '0'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=-10),
            'f', {'f': '-1'})

    def test_error_not_integer(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': 'foo'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1.0'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1e'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Exception, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {})

class FloatValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.FloatValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, input_style="-1234.5"),
            'f', {'f': '15.5'})
        self.assertEqual(15.5, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, input_style="-1234.5"),
            'f', {'f': '15.0'})
        self.assertEqual(15.0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, input_style="-1234.5"),
            'f', {'f': '15'})
        self.assertEqual(15.0, result)

    def test_error_not_float(self):
        self.assertValidatorRaises(
           Validator.ValidationError, 'not_float',
           self.v.validate,
           TestField('f', max_length=0, truncate=0,
                     required=1, input_style="-1234.5"),
           'f', {'f': '1f'})

class DateTimeValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.DateTimeValidatorInstance

    def test_normal(self):
        result = self.v.validate(
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

    def test_ampm(self):
        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'am'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'pm'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(22, result.hour())
        self.assertEqual(30, result.minute())

        self.assertValidatorRaises(
            KeyError, 'not_datetime',
            self.v.validate,
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})

    def test_date_only(self):
        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

    def test_allow_empty_time(self):
        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1, date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(0, result.hour())
        self.assertEqual(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEqual(2002, result.year())
        self.assertEqual(12, result.month())
        self.assertEqual(1, result.day())
        self.assertEqual(10, result.hour())
        self.assertEqual(30, result.minute())

class LinesValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.LinesValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f',),
            'f', {'f' : 'foo\r\nbar'})
        self.assertEqual(['foo', 'bar'], result)

    def test_preserve_whitespace(self):
        result = self.v.validate(
            TestField('f', whitespace_preserve=True),
            'f', {'f' : 'foo\r\nbar '})
        self.assertEqual(['foo', 'bar '], result)

    def test_empty_lines(self):
        result = self.v.validate(
            TestField('f', whitespace_preserve=True),
            'f', {'f' : '\r\nfoo\r\n\r\nbar\r\n'})
        self.assertEqual(['', 'foo', '', 'bar', ''], result)

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(StringValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BooleanValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(IntegerValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(FloatValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(DateTimeValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(LinesValidatorTestCase, 'test'))

    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()

