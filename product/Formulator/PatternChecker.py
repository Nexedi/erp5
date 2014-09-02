import re

# Symbols that are used to represent groups of characters

NUMBERSYMBOL  = 'd'             # 0-9
CHARSYMBOL    = 'e'             # a-zA-Z
NUMCHARSYMBOL = 'f'             # a-zA-Z0-9

# List of characters, that are special to Regex. Listing them here and
# therefore escaping them will help making the Validator secure.
# NOTE: Please do not add '*', since it is used to determine inifinite
# long char symbol rows. (See examples at the of the file.)

DANGEROUSCHARS = '\\()+?.$'

class PatternChecker:
    """
    This class defines a basic user friendly checker and processor of
    string values according to pattern.
    It can verify whether a string value fits a certain pattern of
    digits and letters and possible special characters.
    """
    # a dictionary that converts an array of symbols to regex expressions
    symbol_regex_dict = {NUMBERSYMBOL  : '([0-9]{%i,%s})',
                         CHARSYMBOL    : '([a-zA-Z]{%i,%s})',
                         NUMCHARSYMBOL : '([0-9a-zA-Z]{%i,%s})'}

    def _escape(self, match_object):
        """Escape a single character.
        """
        return '\\' + match_object.group(0)

    def _escape_special_characters(self, s):
        """Escape the characters that have a special meaning in regex.
        """
        return re.sub('[' + DANGEROUSCHARS + ']', self._escape, s)

    def _unescape_special_characters(self, s):
        """Reverse the escaping, so that the final string is as close as
        possible to the original one.
        """
        return re.sub('\\\\', '', s)

    def _replace_symbol_by_regex(self, match_object):
        """Replace the character symbol with their respective regex.
        """
        length = len(match_object.group(0))

        # Yikes, what a hack! But I could not come up with something better.
        if match_object.group(0)[-1] == '*':
            min = length - 1
            max = ''
        else:
            min = length
            max = str(min)

        return self.symbol_regex_dict[match_object.group(0)[0]] %(min, max)

    def make_regex_from_pattern(self, pattern):
        """Replaces all symbol occurences and creates a complete regex
        string.
        """
        regex = self._escape_special_characters(pattern)
        for symbol in [NUMBERSYMBOL, CHARSYMBOL, NUMCHARSYMBOL]:
            regex = re.sub(symbol+'{1,}\*?', self._replace_symbol_by_regex, regex)
        return '^ *' + regex + ' *$'

    def construct_value_from_match(self, result, pattern):
        """After we validated the string, we put it back together; this is
        good, since we can easily clean up the data this way.
        """
        value = self._escape_special_characters(pattern)
        _symbols = '['+NUMBERSYMBOL + CHARSYMBOL + NUMCHARSYMBOL + ']'
        re_obj = re.compile(_symbols+'{1,}\*?')
        for res in result.groups():
            match = re_obj.search(value)
            value = value[:match.start()] + res + value[match.end():]
        return value

    def clean_value(self, value):
        """Clean up unnecessary white characters.
        """
        # same as string.strip, but since I am using re everywhere here,
        # why not use it now too?
        value = re.sub('^\s*', '', value)
        value = re.sub('\s*$', '', value)
        # make out of several white spaces, one whitespace...
        value = re.sub('  *', ' ', value)
        return value

    def validate_value(self, patterns, value):
        """Validate method that manges the entire validation process.

        The validator goes through each pattern and
        tries to get a match to the value (second parameter). At the end, the
        first pattern of the list is taken to construct the value again; this
        ensures data cleansing and a common data look.
        """
        value = self.clean_value(value)

        result = None
        for pattern in patterns:
            regex = self.make_regex_from_pattern(pattern)
            re_obj = re.compile(regex)
            result = re_obj.search(value)
            if result:
                break

        if not result:
            return None

        value = self.construct_value_from_match(result, patterns[0])
        return self._unescape_special_characters(value)

if __name__ == '__main__':

    val = PatternChecker()

    # American long ZIP
    print val.validate_value(['ddddd-dddd'], '34567-1298')
    print val.validate_value(['ddddd-dddd'], '  34567-1298  \t  ')

    # American phone number
    print val.validate_value(['(ddd) ddd-dddd', 'ddd-ddd-dddd',
                              'ddd ddd-dddd'],
                             '(345) 678-1298')
    print val.validate_value(['(ddd) ddd-dddd', 'ddd-ddd-dddd',
                              'ddd ddd-dddd'],
                             '345-678-1298')

    # American money
    print val.validate_value(['$ d*.dd'], '$ 1345345.00')

    # German money
    print val.validate_value(['d*.dd DM'], '267.98 DM')

    # German license plate
    print val.validate_value(['eee ee-ddd'], 'OSL HR-683')

    # German phone number (international)
    print val.validate_value(['+49 (d*) d*'], '+49 (3574) 7253')
    print val.validate_value(['+49 (d*) d*'], '+49  (3574)  7253')









