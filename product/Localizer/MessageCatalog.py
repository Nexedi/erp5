# -*- coding: utf-8 -*-
# Copyright (C) 2000-2007  Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2003  Roberto Quero, Eduardo Corrales
# Copyright (C) 2004  Søren Roug
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides the MessageCatalog base class, which
provides message catalogs for the web.
"""
from __future__ import absolute_import

# Import from the Standard Library
import six
from past.builtins import cmp
from six import string_types as basestring
if six.PY2:
  from base64 import encodestring as encodebytes, decodestring as decodebytes
else:
  from base64 import encodebytes, decodebytes
from hashlib import md5
from re import compile
from time import gmtime, strftime, time
from six.moves.urllib.parse import quote
from traceback import format_list, extract_stack

# Import from polib
import polib

# Import from Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from AccessControl.class_init import InitializeClass
from App.Dialogs import MessageDialog
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from Persistence import PersistentMapping
from ZPublisher import HTTPRequest
from zope.component import getSiteManager
from zope.i18n import interpolate
from zope.i18n.interfaces import ITranslationDomain
from zope.interface import implementer
from zLOG import LOG, INFO
from zExceptions import Forbidden

# Import from Localizer
from .interfaces import IMessageCatalog
from .LanguageManager import LanguageManager
from .LocalFiles import LocalDTMLFile
from .utils import charsets, lang_negotiator, _


###########################################################################
# Utility functions and constants
###########################################################################
def md5text(str):
    """Create an MD5 sum (or hash) of a text. It is guaranteed to be 32 bytes
    long.
    """
    return md5(str.encode('utf-8')).hexdigest()


def to_unicode(x, encoding=None):
    """In Zope the ISO-8859-1 encoding has an special status, normal strings
    are considered to be in this encoding by default.
    """
    if isinstance(x, six.binary_type):
        return six.text_type(x, encoding or HTTPRequest.default_encoding)
    return six.text_type(x)


def to_str(x):
    """Make sure we have an (utf-8 encoded) string"""
    if isinstance(x, str):
        return x
    return x.encode('utf-8')

def message_encode(message):
    """Encodes a message to an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    if isinstance(message, six.text_type):
        encoding = HTTPRequest.default_encoding
        message = message.encode(encoding)

    return encodebytes(message)


def message_decode(message):
    """Decodes a message from an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    message = decodebytes(message.encode())
    encoding = HTTPRequest.default_encoding
    return six.text_type(message, encoding)


def get_url(url, batch_start, batch_size, regex, lang, empty, **kw):
    params = []
    for key, value in six.iteritems(kw):
        if value is None:
            continue
        if isinstance(value, six.text_type):
            value = value.encode('utf-8')
        params.append('%s=%s' % (key, quote(value)))

    params.extend(['batch_start:int=%d' % batch_start,
                   'batch_size:int=%d' % batch_size,
                   'regex=%s' % quote(regex),
                   'empty=%s' % (empty and 'on' or '')])

    if lang:
        params.append('lang=%s' % lang)

    return url + '?' + '&amp;'.join(params)


# Empty header information for PO files (UTF-8 is the default encoding)
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': 'UTF-8'}


###########################################################################
# The Message Catalog class, and ZMI constructor
###########################################################################
manage_addMessageCatalogForm = LocalDTMLFile('ui/MC_add', globals())
def manage_addMessageCatalog(self, id, title, languages, sourcelang=None,
                             REQUEST=None):
    """ """
    if sourcelang is None:
        sourcelang = languages[0]

    self._setObject(id, MessageCatalog(id, title, sourcelang, languages))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)



@implementer(IMessageCatalog)
class MessageCatalog(LanguageManager, ObjectManager, SimpleItem):
    """Stores messages and their translations...
    """

    meta_type = 'MessageCatalog'


    security = ClassSecurityInfo()


    POLICY_ADD_FALSE = 0
    POLICY_ADD_TRUE = 1
    POLICY_ADD_LOG = 2


    def __init__(self, id, title, sourcelang, languages):
        self.id = id

        self.title = title
        self.policy = self.POLICY_ADD_TRUE

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = sourcelang

        # Here the message translations are stored
        self._messages = PersistentMapping()

        # Data for the PO files headers
        self._po_headers = PersistentMapping()
        for lang in self._languages:
            self._po_headers[lang] = empty_po_header


    #######################################################################
    # ITranslationDomain interface
    # zope.i18n.interfaces.ITranslationDomain
    #######################################################################
    @property
    def domain(self):
        """ """
        return six.text_type(self.id)


    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None,
                  # zope i18n 4.7
                  msgid_plural=None, default_plural=None, number=None):
        """ """
        msgstr = self.gettext(msgid, lang=target_language, default=default)
        # BBB support str in mapping by converting to unicode for
        # backward compatibility.
        if mapping:
            mapping = dict([to_unicode(k), to_unicode(v)]
                            for k, v in six.iteritems(mapping))
        return interpolate(msgstr, mapping)


    #######################################################################
    # Private API
    #######################################################################
    def get_message_key(self, message):
        if message in self._messages:
            return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, six.text_type):
            message = message.encode(encoding)
        else:
            message = six.text_type(message, encoding)
        if message in self._messages:
            return message


    def get_translations(self, message):
        message = self.get_message_key(message)
        return self._messages[message]


    def get_tabs_message(self, REQUEST):
        message = REQUEST.get('manage_tabs_message')
        if message is None:
            return None
        return six.text_type(message, 'utf-8')


    #######################################################################
    # Public API
    #######################################################################
    security.declarePublic('message_exists')
    def message_exists(self, message):
        """ """
        # BBB call get_message_key to support both (old) str key and
        # (new) unicode key.
        return bool(self.get_message_key(message))


    security.declareProtected('Manage messages', 'message_edit')
    def message_edit(self, message, language, translation, note):
        """ """
        # BBB call get_message_key to support both (old) str key and
        # (new) unicode key.
        message = self.get_message_key(message) or message
        self._messages[message][language] = translation
        self._messages[message]['note'] = note


    security.declareProtected('Manage messages', 'message_del')
    def message_del(self, message):
        """ """
        # BBB call get_message_key to support both (old) str key and
        # (new) unicode key.
        message = self.get_message_key(message) or message
        del self._messages[message]


    security.declarePublic('gettext')
    def gettext(self, message, lang=None, add=None, default=None):
        """Returns the message translation from the database if available.

        If add=1, add any unknown message to the database.
        If a default is provided, use it instead of the message id
        as a translation for unknown messages.
        """
        if not isinstance(message, basestring):
            raise TypeError('only strings can be translated, not: %r' % (message,))

        if default is None:
            default = message

        message = message.strip()

        # BBB call get_message_key to support both (old) str key and
        # (new) unicode key.
        message = self.get_message_key(message) or to_unicode(message)

        # Add it if it's not in the dictionary
        if add is None:
            add = getattr(self, 'policy', self.POLICY_ADD_TRUE)
        if add != self.POLICY_ADD_FALSE and message not in self._messages and message:
            if add == self.POLICY_ADD_LOG:
                LOG('New entry added to message catalog %s :' % self.id,  INFO, '%s\n%s' % (message, ''.join(format_list(extract_stack()[:-1]))))
            self._messages[message] = PersistentMapping()

        # Get the string
        if message in self._messages:
            m = self._messages[message]

            if lang is None:
                # Builds the list of available languages
                # should the empty translations be filtered?
                available_languages = list(self._languages)

                # Imagine that the default language is 'en'. There is no
                # translation from 'en' to 'en' in the message catalog
                # The user has the preferences 'en' and 'nl' in that order
                # The next two lines make certain 'en' is shown, not 'nl'
                if not self._default_language in available_languages:
                    available_languages.append(self._default_language)

                # Get the language!
                lang = lang_negotiator(available_languages)

                # Is it None? use the default
                if lang is None:
                    lang = self._default_language

            if lang is not None:
                return m.get(lang) or default

        return default


    __call__ = gettext


    #######################################################################
    # Management screens
    #######################################################################
    manage_options = (
        {'label': u'Messages', 'action': 'manage_messages',
         'help': ('Localizer', 'MC_messages.stx')},
        {'label': u'Properties', 'action': 'manage_propertiesForm'},
        {'label': u'Import', 'action': 'manage_Import_form',
         'help': ('Localizer', 'MC_importExport.stx')},
        {'label': u'Export', 'action': 'manage_Export_form',
         'help': ('Localizer', 'MC_importExport.stx')}) \
        + LanguageManager.manage_options \
        + SimpleItem.manage_options


    #######################################################################
    # Management screens -- Messages
    #######################################################################
    security.declareProtected('Manage messages', 'manage_messages')
    manage_messages = LocalDTMLFile('ui/MC_messages', globals())


    security.declarePublic('get_namespace')
    def get_namespace(self, REQUEST):
        """For the management interface, allows to filter the messages to
        show.
        """
        # Check whether there are languages or not
        languages = self.get_languages_mapping()
        if not languages:
            return {}

        # Input
        batch_start = REQUEST.get('batch_start', 0)
        batch_size = REQUEST.get('batch_size', 15)
        empty = REQUEST.get('empty', 0)
        regex = REQUEST.get('regex', '')
        message = REQUEST.get('msg', None)

        # Build the namespace
        namespace = {}
        namespace['batch_size'] = batch_size
        namespace['empty'] = empty
        namespace['regex'] = regex

        # The language
        lang = REQUEST.get('lang', None) or languages[0]['code']
        namespace['language'] = lang

        # Filter the messages
        query = regex.strip()
        try:
            query = compile(query)
        except:
            query = compile('')

        messages = []
        for m, t in six.iteritems(self._messages):
            if query.search(m) and (not empty or not t.get(lang, '').strip()):
                messages.append(m)
        messages.sort(key=lambda m: to_unicode(m))
        # How many messages
        n = len(messages)
        namespace['n_messages'] = n

        # Calculate the start
        while batch_start >= n:
            batch_start = batch_start - batch_size
        if batch_start < 0:
            batch_start = 0
        namespace['batch_start'] = batch_start
        # Select the batch to show
        batch_end = batch_start + batch_size
        messages = messages[batch_start:batch_end]
        # Batch links
        namespace['previous'] = get_url(REQUEST.URL, batch_start - batch_size,
            batch_size, regex, lang, empty)
        namespace['next'] = get_url(REQUEST.URL, batch_start + batch_size,
            batch_size, regex, lang, empty)

        # Get the message
        message_encoded = None
        translations = {}
        if message is None:
            if messages:
                message = messages[0]
                translations = self.get_translations(message)
                message = to_unicode(message)
                message_encoded = message_encode(message)
        else:
            message_encoded = message
            message = message_decode(message_encoded)
            translations = self.get_translations(message)
            message = to_unicode(message)
        namespace['message'] = message
        namespace['message_encoded'] = message_encoded
        namespace['translations'] = translations
        namespace['translation'] = translations.get(lang, '')
        namespace['note'] = translations.get('note', '')

        # Calculate the current message
        namespace['messages'] = []
        for x in messages:
            x = to_unicode(x)
            x_encoded = message_encode(x)
            url = get_url(
                REQUEST.URL, batch_start, batch_size, regex, lang, empty,
                msg=x_encoded)
            namespace['messages'].append({
                'message': x,
                'message_encoded': x_encoded,
                'current': x == message,
                'url': url})

        # The languages
        for language in languages:
            code = language['code']
            language['name'] = _(language['name'], language=code)
            language['url'] = get_url(REQUEST.URL, batch_start, batch_size,
                regex, code, empty, msg=message_encoded)
        namespace['languages'] = languages

        return namespace


    security.declareProtected('Manage messages', 'manage_editMessage')
    def manage_editMessage(self, message, language, translation, note,
                           REQUEST, RESPONSE):
        """Modifies a message.
        """
        message_encoded = message
        message = message_decode(message_encoded)
        message_key = self.get_message_key(message)
        self.message_edit(message_key, language, translation, note)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      msg=message_encoded,
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)


    security.declareProtected('Manage messages', 'manage_delMessage')
    def manage_delMessage(self, message, REQUEST, RESPONSE):
        """ """
        message = message_decode(message)
        message_key = self.get_message_key(message)
        self.message_del(message_key)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)


    #######################################################################
    # Management screens -- Properties
    # Management screens -- Import/Export
    # FTP access
    #######################################################################
    security.declareProtected('View management screens',
                              'manage_propertiesForm')
    manage_propertiesForm = LocalDTMLFile('ui/MC_properties', globals())


    security.declareProtected('View management screens', 'manage_properties')
    def manage_properties(self, title, policy, REQUEST=None, RESPONSE=None):
        """Change the Message Catalog properties.
        """
        self.title = title
        self.policy = int(policy)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')


    # Properties management screen
    security.declareProtected('View management screens', 'get_po_header')
    def get_po_header(self, lang):
        """ """
        # For backwards compatibility
        if not hasattr(aq_base(self), '_po_headers'):
            self._po_headers = PersistentMapping()

        return self._po_headers.get(lang, empty_po_header)


    security.declareProtected('View management screens', 'update_po_header')
    def update_po_header(self, lang,
                         last_translator_name=None,
                         last_translator_email=None,
                         language_team=None,
                         charset=None,
                         REQUEST=None, RESPONSE=None):
        """ """
        header = self.get_po_header(lang)

        if last_translator_name is None:
            last_translator_name = header['last_translator_name']

        if last_translator_email is None:
            last_translator_email = header['last_translator_email']

        if language_team is None:
            language_team = header['language_team']

        if charset is None:
            charset = header['charset']

        header = {'last_translator_name': last_translator_name,
                  'last_translator_email': last_translator_email,
                  'language_team': language_team,
                  'charset': charset}

        self._po_headers[lang] = header

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')



    security.declareProtected('View management screens', 'manage_Import_form')
    manage_Import_form = LocalDTMLFile('ui/MC_Import_form', globals())


    security.declarePublic('get_policies')
    def get_policies(self):
        """ """
        if not hasattr(self, 'policy'):
            self.policy = self.POLICY_ADD_TRUE
        policies = [
            [self.POLICY_ADD_FALSE, "Never add new entries automatically"],
            [self.POLICY_ADD_TRUE, "Add new entries automatically if missing"],
            [self.POLICY_ADD_LOG, "Add new entries automatically if missing and log the backtrace"],
        ]
        return policies


    security.declarePublic('get_charsets')
    def get_charsets(self):
        """ """
        return charsets[:]


    security.declarePublic('manage_export')
    def manage_export(self, x, REQUEST=None, RESPONSE=None):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """
        # Get the PO header info
        header = self.get_po_header(x)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset']

        # PO file header, empty message.
        po_revision_date = strftime('%Y-%m-%d %H:%m+%Z', gmtime(time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if x == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (x, language_team)

        r = ['msgid ""',
             'msgstr "Project-Id-Version: %s\\n"' % self.title,
             '"POT-Creation-Date: %s\\n"' % pot_creation_date,
             '"PO-Revision-Date: %s\\n"' % po_revision_date,
             '"Last-Translator: %s\\n"' % last_translator,
             '"Language-Team: %s\\n"' % language_team,
             '"MIME-Version: 1.0\\n"',
             '"Content-Type: text/plain; charset=%s\\n"' % charset,
             '"Content-Transfer-Encoding: 8bit\\n"',
             '', '']


        # Get the messages, and perhaps its translations.
        # Convert keys to unicode for proper sorting.
        d = {}
        if x == 'locale.pot':
            filename = x
            for k in six.iterkeys(self._messages):
                d[to_unicode(k, encoding=charset)] = u""
        else:
            filename = '%s.po' % x
            for k, v in six.iteritems(self._messages):
                k = to_unicode(k, encoding=charset)
                d[k] = to_unicode(v.get(x, ""), encoding=charset)

        # Generate the file
        def backslashescape(x):
            x = to_str(x)
            quote_esc = compile(r'"')
            x = quote_esc.sub('\\"', x)

            trans = [('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
            for a, b in trans:
                x = x.replace(a, b)

            return x

        # Generate sorted msgids to simplify diffs
        for k, v in sorted(six.iteritems(d)):
            r.append('msgid "%s"' % backslashescape(k))
            r.append('msgstr "%s"' % backslashescape(v))
            r.append('')

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-type','application/data')
            RESPONSE.setHeader('Content-Disposition',
                               'inline;filename=%s' % filename)

        return '\n'.join(r)


    security.declareProtected('Manage messages', 'po_import')
    def po_import(self, lang, data):
        """ """
        messages = self._messages

        # Load the data
        if isinstance(data, bytes): # six.PY2
            pass
        elif isinstance(data, bytes): # six.PY3
            data = data.decode()
        po = polib.pofile(data)
        encoding = to_str(po.encoding)
        for entry in po:
            msgid = to_unicode(entry.msgid, encoding=encoding)
            if msgid:
                msgstr = to_unicode(entry.msgstr or '', encoding=encoding)
                translation_map = messages.get(msgid)
                if translation_map is None:
                    # convert old non-unicode translations if they exist:
                    translation_map = messages.pop(self.get_message_key(msgid),
                                                   None)
                    if translation_map is None:
                        translation_map = PersistentMapping()
                    messages[msgid] = translation_map
                translation_map[lang] = msgstr

        # Set the encoding (the full header should be loaded XXX)
        self.update_po_header(lang, charset=encoding)


    security.declareProtected('Manage messages', 'manage_import')
    def manage_import(self, lang, file, REQUEST=None, RESPONSE=None):
        """ """
        # XXX For backwards compatibility only, use "po_import" instead.
        if isinstance(file, str): # six.PY2
            content = file
        elif isinstance(file, bytes): # six.PY3
            content = file.decode()
        else:
            content = file.read()

        self.po_import(lang, content)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_messages')


    def objectItems(self, spec=None):
        """ """
        for lang in self._languages:
            if not hasattr(aq_base(self), lang):
                self._setObject(lang, POFile(lang))

        r = MessageCatalog.inheritedAttribute('objectItems')(self, spec)
        return r


    #######################################################################
    # TMX support
    security.declareProtected('View management screens', 'manage_Export_form')
    manage_Export_form = LocalDTMLFile('ui/MC_Export_form', globals())


    #######################################################################
    # Backwards compatibility (XXX)
    #######################################################################

    security.declarePublic('hasmsg')
    hasmsg = message_exists
    security.declarePublic('hasLS')
    hasLS = message_exists  # CMFLocalizer uses it

class POFile(SimpleItem):
    """ """

    security = ClassSecurityInfo()


    def __init__(self, id):
        self.id = id


    security.declareProtected('FTP access', 'manage_FTPget')
    def manage_FTPget(self):
        """ """
        return self.manage_export(self.id)


    security.declareProtected('Manage messages', 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ """
        if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
            raise Forbidden('REQUEST_METHOD should be PUT.')
        body = REQUEST['BODY']
        self.po_import(self.id, body)
        RESPONSE.setStatus(204)
        return RESPONSE

InitializeClass(MessageCatalog)
InitializeClass(POFile)


# This dict define the alias between old Translation Service catalog id
#   and new Localizer Message Catalog.
message_catalog_aliases = { "Default": "default"
                          , "ui"     : "erp5_ui"
                          , "content": "erp5_content"
                          }

# "invert" message_catalog_aliases mapping
message_catalog_alias_sources = {}
for name, value in six.iteritems(message_catalog_aliases):
    message_catalog_alias_sources.setdefault(value, []).append(name)

def MessageCatalog_moved(object, event):
    # FIXME This does not work if what we move is the folder that contains
    # the message catalog
    container = event.oldParent
    if container is not None:
        sm = getSiteManager(container)
        sm.unregisterUtility(object, ITranslationDomain, event.oldName)
        # unregister old aliases
        oldAliases = message_catalog_alias_sources.get(event.oldName, ())
        sm = getSiteManager(event.oldParent)
        for alias in oldAliases:
            sm.unregisterUtility(object, ITranslationDomain, alias)

    container = event.newParent
    if container is not None:
        sm = getSiteManager(container)
        sm.registerUtility(object, ITranslationDomain, event.newName)

        # register new aliases
        newAliases = message_catalog_alias_sources.get(event.newName, ())
        sm = getSiteManager(event.newParent)
        for alias in newAliases:
            sm.registerUtility(object, ITranslationDomain, alias)
