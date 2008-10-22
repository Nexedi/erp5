import logging
from sgmllib import SGMLParser

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.utils import log
from Products.CMFDefault.utils import bodyfinder
from Products.CMFDefault.utils import IllegalHTML
from Products.CMFDefault.utils import SimpleHTMLParser
from Products.CMFDefault.utils import VALID_TAGS
from Products.CMFDefault.utils import NASTY_TAGS

# tag mapping: tag -> short or long tag
VALID_TAGS = VALID_TAGS.copy()
NASTY_TAGS = NASTY_TAGS.copy()

# add some tags to allowed types. This should be fixed in CMFDefault
VALID_TAGS['ins'] = 1
VALID_TAGS['del'] = 1
VALID_TAGS['q'] = 1
VALID_TAGS['map']=1
VALID_TAGS['area']=1

msg_pat = """
<div class="system-message">
<p class="system-message-title">System message: %s</p>
%s</d>
"""

class StrippingParser(SGMLParser):
    """Pass only allowed tags;  raise exception for known-bad.

    Copied from Products.CMFDefault.utils
    Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
    """

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__(self, valid, nasty, remove_javascript, raise_error):
        SGMLParser.__init__( self )
        self.result = []
        self.valid = valid
        self.nasty = nasty
        self.remove_javascript = remove_javascript
        self.raise_error = raise_error
        self.suppress = False

    def handle_data(self, data):
        if self.suppress: return
        if data:
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
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result.append('&%s%s' % (name, x))

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones.
        """

        if self.suppress: return
        #if self.remove_javascript and tag == script and :

        if self.valid.has_key(tag):
            self.result.append('<' + tag)

            for k, v in attrs:
                if self.remove_javascript and k.strip().lower().startswith('on'):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Javascript event "%s" not allowed.' % k
                elif self.remove_javascript and v.strip().lower().startswith('javascript:' ):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Javascript URI "%s" not allowed.' % v
                else:
                    self.result.append(' %s="%s"' % (k, v))

            #UNUSED endTag = '</%s>' % tag
            if self.valid.get(tag):
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

    def unknown_endtag(self, tag):
        if self.nasty.has_key(tag):
            self.suppress = False
        if self.suppress: return
        if self.valid.get(tag):
            self.result.append('</%s>' % tag)
            #remTag = '</%s>' % tag

    def getResult(self):
        return ''.join(self.result)

def scrubHTML(html, valid=VALID_TAGS, nasty=NASTY_TAGS,
              remove_javascript=True, raise_error=True):

    """ Strip illegal HTML tags from string text.
    """
    parser = StrippingParser(valid=valid, nasty=nasty,
                             remove_javascript=remove_javascript,
                             raise_error=raise_error)
    parser.feed(html)
    parser.close()
    return parser.getResult()

class SafeHTML:
    """Simple transform which uses CMFDefault functions to
    clean potentially bad tags.
    Tags must explicit be allowed in valid_tags to pass. Only the tags
    themself are removed, not their contents. If tags are
    removed and in nasty_tags, they are removed with
    all of their contents.
    Be aware that you may need to clean the cache to let a Object
    call the transform again.
    """

    __implements__ = itransform

    __name__ = "safe_html"
    inputs   = ('text/html',)
    output = "text/x-html-safe"

    def __init__(self, name=None, **kwargs):


        self.config = {
            'inputs': self.inputs,
            'output': self.output,
            'valid_tags': VALID_TAGS,
            'nasty_tags': NASTY_TAGS,
            'remove_javascript': 1,
            'disable_transform': 0,
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
            'remove_javascript' : ("int",
                                   'remove_javascript',
                                   '1 to remove javascript attributes that begin with on (e.g. onClick) ' +
                                   'and attributes where the value starts with "javascript:" ' +
                                   '(e.g. <a href="javascript:function()". ' +
                                   'This does not effect <script> tags. 0 to leave the attributes.'),
            'disable_transform' : ("int",
                                   'disable_transform',
                                   'If 1, nothing is done.')
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
            log(logging.ERROR, 'PortalTransforms safe_html transform needs to be '
                'updated. Please re-install the PortalTransforms product to fix.')

        # if we have a config that we don't want to delete
        # we need a disable option
        if self.config.get('disable_transform'):
            data.setData(orig)
            return data

        try:
            safe = scrubHTML(
                bodyfinder(orig),
                valid=self.config.get('valid_tags', {}),
                nasty=self.config.get('nasty_tags', {}),
                remove_javascript=self.config.get('remove_javascript', True),
                raise_error=False)
        except IllegalHTML, inst:
            data.setData(msg_pat % ("Error", str(inst)))
        else:
            data.setData(safe)
        return data

def register():
    return SafeHTML()
