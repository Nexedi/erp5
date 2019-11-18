# -*- coding: utf-8 -*-
from zLOG import ERROR
from HTMLParser import HTMLParser, HTMLParseError
import re
from cgi import escape
import codecs

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.libtransforms.utils import IllegalHTML
from Products.PortalTransforms.utils import safeToInt

from lxml import etree
from lxml.etree import HTMLParser as LHTMLParser
from lxml.html import tostring

try:
  from lxml.html.soupparser import fromstring as soupfromstring
except ImportError:
  # Means BeautifulSoup module is not installed
  soupfromstring = None
# tag mapping: tag -> short or long tag
VALID_TAGS = {
  'a': 1,
  'b': 1,
  'base': 0,
  'big': 1,
  'blockquote': 1,
  'body': 1,
  'br': 0,
  'caption': 1,
  'cite': 1,
  'code': 1,
  'dd': 1,
  'div': 1,
  'dl': 1,
  'dt': 1,
  'em': 1,
  'font': 1,
  'h1': 1,
  'h2': 1,
  'h3': 1,
  'h4': 1,
  'h5': 1,
  'h6': 1,
  'head': 1,
  'hr': 0,
  'html': 1,
  'i': 1,
  'img': 0,
  'kbd': 1,
  'li': 1,
#  'link': 1, type="script" hoses us
  'meta': 0,
  'ol': 1,
  'p': 1,
  'pre': 1,
  'small': 1,
  'span': 1,
  'strong': 1,
  'sub': 1,
  'sup': 1,
  'table': 1,
  'tbody': 1,
  'td': 1,
  'th': 1,
  'title': 1,
  'tr': 1,
  'tt': 1,
  'u': 1,
  'ul': 1,
  }

NASTY_TAGS = {
  'script': 1,
  'object': 1,
  'embed': 1,
  'applet': 1,
  }

# add some tags to allowed types.
VALID_TAGS['ins'] = 1
VALID_TAGS['del'] = 1
VALID_TAGS['q'] = 1
VALID_TAGS['map'] = 1
VALID_TAGS['area'] = 0
VALID_TAGS['abbr'] = 1
VALID_TAGS['acronym'] = 1
VALID_TAGS['var'] = 1
VALID_TAGS['dfn'] = 1
VALID_TAGS['samp'] = 1
VALID_TAGS['address'] = 1
VALID_TAGS['bdo'] = 1
VALID_TAGS['thead'] = 1
VALID_TAGS['tfoot'] = 1
VALID_TAGS['col'] = 1
VALID_TAGS['colgroup'] = 1

# HTML5 tags that should be allowed:
VALID_TAGS['article'] = 1
VALID_TAGS['aside'] = 1
VALID_TAGS['audio'] = 1
VALID_TAGS['canvas'] = 1
VALID_TAGS['command'] = 1
VALID_TAGS['datalist'] = 1
VALID_TAGS['details'] = 1
VALID_TAGS['dialog'] = 1
VALID_TAGS['figure'] = 1
VALID_TAGS['footer'] = 1
VALID_TAGS['header'] = 1
VALID_TAGS['hgroup'] = 1
VALID_TAGS['keygen'] = 1
VALID_TAGS['mark'] = 1
VALID_TAGS['meter'] = 1
VALID_TAGS['nav'] = 1
VALID_TAGS['output'] = 1
VALID_TAGS['progress'] = 1
VALID_TAGS['rp'] = 1
VALID_TAGS['rt'] = 1
VALID_TAGS['ruby'] = 1
VALID_TAGS['section'] = 1
VALID_TAGS['source'] = 1
VALID_TAGS['summary'] = 1
VALID_TAGS['time'] = 1
VALID_TAGS['video'] = 1

# Selenium tests
VALID_TAGS['test'] = 1

# add some tags to nasty.
NASTY_TAGS['style'] = 1  # this helps improve Word HTML cleanup.
NASTY_TAGS['meta'] = 1  # allowed by parsers, but can cause unexpected behavior


msg_pat = """
<div class="system-message">
<p class="system-message-title">System message: %s</p>
%s</d>
"""

# we inconditionally remove all meta tags with http-equiv
# except for content-type, because:
# * refresh can redirect;
# * set-cookie expose confidential data;
# * www-authenticate can disturb authentication on portal;
# * expires can disbale caching features
# * ...
ALLOWED_HTTP_EQUIV_VALUE_LIST = ('content-type',)

def hasScript(s):
   """Dig out evil Java/VB script inside an HTML attribute.

   >>> hasScript('script:evil(1);')
   True
   >>> hasScript('expression:evil(1);')
   True
   >>> hasScript('http://foo.com/ExpressionOfInterest.doc')
   False
   """
   s = decode_htmlentities(s)
   s = ''.join(s.split()).lower()
   for t in ('script:', 'expression:', 'expression('):
      if t in s:
         return True
   return False

def decode_htmlentities(s):
   """ XSS code can be hidden with htmlentities """

   entity_pattern = re.compile("&#(?P<htmlentity>x?\w+)?;?")
   s = entity_pattern.sub(decode_htmlentity,s)
   return s

def decode_htmlentity(m):
   entity_value = m.groupdict()['htmlentity']
   try:
      if entity_value[0] in ['x','X']:
         c = int(entity_value[1:], 16)
      else:
         c = int(entity_value)
      return unichr(c)
   except ValueError:
      return entity_value

charset_parser = re.compile('charset="?(?P<charset>[^"]*)"?[\S/]?',
                            re.IGNORECASE)
class CharsetReplacer:
  def __init__(self, encoding):
    self.encoding = encoding

  def __call__(self, match):
    if match is None:
      return ''
    charset = match.group('charset')
    if charset != self.encoding:
      return match.group(0).replace(charset, self.encoding)
    return match.group(0)

class StrippingParser(HTMLParser):
    """Pass only allowed tags;  raise exception for known-bad.

    Copied from Products.CMFDefault.utils
    Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
    """

    def __init__(self, valid, nasty, remove_javascript, raise_error,
                 default_encoding):
        HTMLParser.__init__( self )
        self.result = []
        self.valid = valid
        self.nasty = nasty
        self.remove_javascript = remove_javascript
        self.raise_error = raise_error
        self.suppress = False
        self.default_encoding = default_encoding
        self.original_charset = None

    def handle_data(self, data):
        if self.suppress: return
        data = escape(data)
        if self.original_charset and isinstance(data, str):
            data = data.decode(self.original_charset)
        self.result.append(data)

    def handle_charref(self, name):
        if self.suppress: return
        self.result.append('&#%s;' % name)

    def handle_comment(self, comment):
        pass

    def handle_decl(self, data):
        pass

    def handle_entityref(self, name):
        if self.suppress: return
        # (begin) copied from Python-2.6's HTMLParser.py
        # Cannot use name2codepoint directly, because HTMLParser supports apos,
        # which is not part of HTML 4
        if getattr(self, 'entitydefs', None) is None:
            import htmlentitydefs
            entitydefs = HTMLParser.entitydefs = {'apos':u"'"}
            for k, v in htmlentitydefs.name2codepoint.iteritems():
                entitydefs[k] = unichr(v)
        # (end) copied from Python-2.6's HTMLParser.py
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result.append('&%s%s' % (name, x))

    def handle_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones.
        """
        if self.suppress: return

        if tag.lower() == 'meta':
          for k, v in attrs:
            if k.lower() == 'http-equiv' and v.lower() not in\
                                                 ALLOWED_HTTP_EQUIV_VALUE_LIST:
              return
        if self.valid.has_key(tag):
            self.result.append('<' + tag)

            remove_script = getattr(self,'remove_javascript',True)

            for k, v in attrs:
                if remove_script and k.strip().lower().startswith('on'):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Script event "%s" not allowed.' % k
                elif v is None:
                    self.result.append(' %s' % k)
                elif remove_script and hasScript(v) and \
                        not (k.lower() == 'src' and tag.lower() == 'img'):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Script URI "%s" not allowed.' % v
                else:
                    if tag.lower() == 'meta' and k.lower() == 'content' and \
                     self.default_encoding and self.default_encoding not in v:
                        match = charset_parser.search(v)
                        if match is not None:
                            charset = match.group('charset')
                            try:
                                codecs.lookup(charset)
                            except LookupError:
                                # If a codec is not known by python, it is better
                                # to prevent it's usage
                                charset = None
                            self.original_charset = charset
                        v = charset_parser.sub(
                            CharsetReplacer(self.default_encoding), v)
                    self.result.append(' %s="%s"' % (k, escape(v, True)))

            #UNUSED endTag = '</%s>' % tag
            if safeToInt(self.valid.get(tag)):
                self.result.append('>')
            else:
                self.result.append(' />')
        elif self.nasty.has_key(tag):
            self.suppress = True
            if self.raise_error:
                raise IllegalHTML, 'Dynamic tag "%s" not allowed.' % tag
        else:
            # omit tag
            pass

    def handle_endtag(self, tag):
        if self.nasty.has_key(tag) and not self.valid.has_key(tag):
            self.suppress = False
        if self.suppress: return
        if safeToInt(self.valid.get(tag)):
            self.result.append('</%s>' % tag)
            #remTag = '</%s>' % tag

    def parse_declaration(self, i):
        """Fix handling of CDATA sections. Code borrowed from BeautifulSoup.
        """
        j = None
        if self.rawdata[i:i+9] == '<![CDATA[':
             k = self.rawdata.find(']]>', i)
             if k == -1:
                 k = len(self.rawdata)
             data = self.rawdata[i+9:k]
             j = k+3
             if self.original_charset and isinstance(data, str):
                 data = data.decode(self.original_charset)
             self.result.append("<![CDATA[%s]]>" % data)
        else:
            try:
                j = HTMLParser.parse_declaration(self, i)
            except HTMLParseError:
                toHandle = self.rawdata[i:]
                self.result.append(toHandle)
                j = i + len(toHandle)
        return j

    def getResult(self):
        return ''.join(self.result)

    def feed(self, html):
      # BBB: Python 2.7 is more tolerant to broken HTML.
      #      For the moment, be strict to behave like Python 2.6.
      HTMLParser.feed(self, html)
      if self.rawdata:
        raise HTMLParseError("unknown error", self.getpos())

def scrubHTML(html, valid=VALID_TAGS, nasty=NASTY_TAGS,
              remove_javascript=True, raise_error=True,
              default_encoding=None):

    """ Strip illegal HTML tags from string text.
    """

    parser = StrippingParser(valid=valid, nasty=nasty,
                             remove_javascript=remove_javascript,
                             raise_error=raise_error,
                             default_encoding=default_encoding)
    # HTMLParser is affected by a known bug referenced
    # by http://bugs.python.org/issue3932
    # As suggested by python developpers:
    # "Python 3.0 implicitly rejects non-unicode strings"
    # We try to decode strings against provided codec first
    if isinstance(html, str):
      try:
        html = html.decode(default_encoding)
      except UnicodeDecodeError:
        pass
    parser.feed(html)
    parser.close()
    result = parser.getResult()
    if parser.original_charset and isinstance(result, str):
        result = result.decode(parser.original_charset).encode(default_encoding)
    return result

class SafeHTML:
    """Simple transform which uses CMFDefault functions to
    clean potentially bad tags.

    Tags must explicit be allowed in valid_tags to pass. Only
    the tags themself are removed, not their contents. If tags
    are removed and in nasty_tags, they are removed with
    all of their contents.

    Objects will not be transformed again with changed settings.
    You need to clear the cache by e.g.
    1.) restarting your zope or
    2.) empty the zodb-cache via ZMI -> Control_Panel
        -> Database Management -> main || other_used_database
        -> Flush Cache.
    """

    implements(ITransform)

    __name__ = "safe_html"
    inputs   = ('text/html',)
    output = "text/x-html-safe"

    def __init__(self, name=None, **kwargs):


        self.config = {
            'inputs': self.inputs,
            'output': self.output,
            'valid_tags': VALID_TAGS,
            'nasty_tags': NASTY_TAGS,
            'stripped_attributes': ['lang','valign','halign','border','frame','rules','cellspacing','cellpadding','bgcolor'],
            'stripped_combinations': {'table th td': 'width height'},
            'style_whitelist': ['text-align', 'list-style-type', 'float'],
            'class_blacklist': [],
            'remove_javascript': 1,
            'disable_transform': 0,
            'default_encoding': 'utf-8',
            }

        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'valid_tags' : ('dict',
                            'valid_tags',
                            'List of valid html-tags, value is 1 if they ' +
                            'have a closing part (e.g. <p>...</p>) and 0 for empty ' +
                            'tags (like <br />). Be carefull!',
                            ('tag', 'value')),
            'nasty_tags' : ('dict',
                            'nasty_tags',
                            'Dynamic Tags that are striped with ' +
                            'everything they contain (like applet, object). ' +
                            'They are only deleted if they are not marked as valid_tags.',
                            ('tag', 'value')),
            'stripped_attributes': ('list',
                                    'stripped_attributes',
                                    'These attributes are stripped from any tag.'),
            'stripped_combinations' : ('dict',
                                       'stripped_combinations',
                                       'These attributes are stripped from any tag.',
                                       ('tag', 'value')),
            'style_whitelist': ('list',
                                'style_whitelist',
                                'These CSS styles are allowed in style attributes.'),
            'class_blacklist': ('list',
                                'class_blacklist',
                                'These class names are not allowed in class attributes.'),
            'remove_javascript' : ("int",
                                   'remove_javascript',
                                   '1 to remove javascript attributes that begin with on (e.g. onClick) ' +
                                   'and attributes where the value starts with "javascript:" ' +
                                   '(e.g. <a href="javascript:function()". ' +
                                   'This does not effect <script> tags. 0 to leave the attributes.'),
            'disable_transform' : ("int",
                                   'disable_transform',
                                   'If 1, nothing is done.'),
            'default_encoding': ('string',
                                 'default_encoding',
                                 'Encoding used for html string.'\
                                     ' If encoding is different, the string will be converted' ),
            }

        self.config.update(kwargs)

        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        # note if we need an upgrade.
        if not self.config.has_key('disable_transform'):
            log(ERROR, 'PortalTransforms safe_html transform needs to be '
                'updated. Please re-install the PortalTransforms product to fix.')

        # if we have a config that we don't want to delete
        # we need a disable option
        if self.config.get('disable_transform'):
            data.setData(orig)
            return data

        repaired = 0
        while True:
            try:
                # Do 2 passes. This provides more reliable filtering of certain
                # malicious HTML (cf upstream commit svn10522).
                for repeat in range(2): orig = scrubHTML(
                    orig,
                    valid=self.config.get('valid_tags', {}),
                    nasty=self.config.get('nasty_tags', {}),
                    remove_javascript=self.config.get('remove_javascript', True),
                    raise_error=False,
                    default_encoding=self.config.get('default_encoding', 'utf-8'))
            except IllegalHTML, inst:
                data.setData(msg_pat % ("Error", str(inst)))
                break
            except (HTMLParseError, UnicodeDecodeError):
                if repeat:
                    raise # try to repair only on first pass
                # ouch !
                # HTMLParser is not able to parse very dirty HTML string
                if not repaired:
                    # try to repair any broken html with help of lxml
                    encoding = kwargs.get('encoding')
                    # recover parameter is equal to True by default
                    # in lxml API. I pass the argument to improve readability
                    # of above code.
                    try:
                        lparser = LHTMLParser(encoding=encoding, recover=True,
                                              remove_comments=True)
                    except LookupError:
                        # Provided encoding is not known by parser so discard it
                        lparser = LHTMLParser(recover=True,
                                              remove_comments=True)
                    repaired_html_tree = etree.HTML(orig, parser=lparser)
                elif repaired > (soupfromstring is not None):
                    # Neither lxml nor BeautifulSoup worked so give up !
                    raise
                else:
                    # Can BeautifulSoup perform miracles ?
                    # This function may raise HTMLParseError.
                    # So consider this parsing as last chance
                    # to get parsable html.
                    repaired_html_tree = soupfromstring(orig)
                orig = tostring(repaired_html_tree,
                                include_meta_content_type=True,
                                method='xml')
                repaired += 1
                # avoid breaking now.
                # continue into the loop with repaired html
            else:
                if isinstance(orig, unicode):
                  orig = orig.encode('utf-8')
                data.setData(orig)
                break
        return data

def register():
    return SafeHTML()
