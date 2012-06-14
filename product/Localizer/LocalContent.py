# -*- coding: UTF-8 -*-
# Copyright (C) 2000-2005  Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from the Standard Library
from hashlib import md5

# Import from itools
from itools.datatypes import LanguageTag
from itools.tmx import TMXFile, Sentence, TMXUnit
from itools.xliff import XLFFile

# Import from Zope
from Acquisition import aq_base, aq_parent
from App.class_init import InitializeClass
from App.Dialogs import MessageDialog
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from AccessControl import ClassSecurityInfo

# Import from Localizer
from LocalAttributes import LocalAttribute
from LocalFiles import LocalDTMLFile
from LocalPropertyManager import LocalPropertyManager
from utils import _


def md5text(str):
    """Create an MD5 sum (or hash) of a text. It is guaranteed to be 32 bytes
    long.
    """
    return md5(str.encode('utf-8')).hexdigest()


manage_addLocalContentForm = LocalDTMLFile('ui/LocalContent_add', globals())
def manage_addLocalContent(self, id, sourcelang, languages, REQUEST=None):
    """ """
    languages.append(sourcelang)   # Make sure source is one of the target langs
    self._setObject(id, LocalContent(id, sourcelang, tuple(languages)))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class LocalContent(CatalogAware, LocalPropertyManager, PropertyManager,
                   SimpleItem):
    """ """

    meta_type = 'LocalContent'

    security = ClassSecurityInfo()

    # Properties metadata
    _local_properties_metadata = ({'id': 'title', 'type': 'string'},
                                  {'id': 'body', 'type': 'text'})

    _properties = ()

    title = LocalAttribute('title')   # Override title from SimpleItem
    body = LocalAttribute('body')


    manage_options = \
        LocalPropertyManager.manage_options \
        + PropertyManager.manage_options[:1] \
        + ({'action': 'manage_import', 'label': u'Import',
            'help': ('Localizer', 'MC_importExport.stx')},
           {'action': 'manage_export', 'label': u'Export',
            'help': ('Localizer', 'MC_importExport.stx')}) \
        + PropertyManager.manage_options[1:] \
        + SimpleItem.manage_options


    def __init__(self, id, sourcelang, languages):
        self.id = id
        self._default_language = sourcelang
        self._languages = languages


    index_html = None     # Prevent accidental acquisition


    def __call__(self, client=None, REQUEST=None, RESPONSE=None, **kw):
        if REQUEST is None:
            REQUEST = self.REQUEST

        # Get the template to use
        template_id = 'default_template'
        if hasattr(aq_base(self), 'default_template'):
            template_id = self.default_template

        # Render the object
        template = getattr(aq_parent(self), template_id)
        template = template.__of__(self)
        return apply(template, ((client, self), REQUEST), kw)


    # Override some methods to be sure that LocalContent objects are
    # reindexed when changed.
    def set_localpropvalue(self, id, lang, value):
        LocalContent.inheritedAttribute('set_localpropvalue')(self, id, lang,
                                                              value)

        self.reindex_object()


    def del_localproperty(self, id):
        LocalContent.inheritedAttribute('del_localproperty')(self, id)

        self.reindex_object()

    security.declareProtected('View management screens', 'manage_import')
    manage_import = LocalDTMLFile('ui/LC_import_form', globals())

    #######################################################################
    # TMX support
    security.declareProtected('View management screens', 'manage_export')
    manage_export = LocalDTMLFile('ui/LC_export_form', globals())

    security.declareProtected('Manage messages', 'tmx_export')
    def tmx_export(self, REQUEST, RESPONSE):
        """Exports the content of the message catalog to a TMX file.
        """

        src_lang = self._default_language

        # Init the TMX handler
        tmx = TMXFile()
        tmx.header['creationtool'] = u'Localizer'
        tmx.header['creationtoolversion'] = u'1.x'
        tmx.header['datatype'] = u'plaintext'
        tmx.header['segtype'] = u'paragraph'
        tmx.header['adminlang'] = src_lang
        tmx.header['srclang'] = src_lang
        tmx.header['o-encoding'] = u'utf-8'

        # Add the translation units
        for key in self._local_properties.keys():
            unit = TMXUnit({})
            for lang in self._languages:
                sentence = Sentence({'lang': lang})
                trans, fuzzy = self.get_localproperty(key, lang)
                sentence.text = trans
                unit.msgstr[lang] = sentence
            tmx.messages[self.get_localproperty(key, src_lang)[0]] = unit

        # Serialize
        data = tmx.to_str()
        # Set response headers
        RESPONSE.setHeader('Content-type','application/data')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s.tmx"' % self.id)
        # Ok
        return data



    security.declareProtected('Manage messages', 'tmx_import')
    def tmx_import(self, file, REQUEST=None, RESPONSE=None):
        """Imports a TMX level 1 file.
        """
        try:
            data = file.read()
            tmx = TMXFile(string=data)
        except:
            return MessageDialog(title = 'Parse error',
                               message = _('impossible to parse the file') ,
                               action = 'manage_import',)

        for id, msg in tmx.messages.items():
            for prop, d in self._local_properties.items():
                if d[self._default_language][0] == id:
                    msg.msgstr.pop(self._default_language)
                    for lang in msg.msgstr.keys():
                        # normalize the languageTag and extract the core
                        (core, local) = LanguageTag.decode(lang)
                        lang = LanguageTag.encode((core, local))
                        if lang not in self._languages:
                            self._languages += (lang,)
                        texte = msg.msgstr[lang].text
                        if texte:
                            self.set_localpropvalue(prop, lang, texte)
                            if core != lang and core != self._default_language:
                                if core not in self._languages:
                                    self._languages += (core,)
                                if not msg.msgstr.has_key(core):
                                    self.set_localpropvalue(prop, lang, texte)

        if REQUEST is not None:
            RESPONSE.redirect('manage_localPropertiesForm')



    security.declareProtected('Manage messages', 'xliff_export')
    def xliff_export(self, dst_lang, export_all=1, REQUEST=None,
                     RESPONSE=None):
        """ Exports the content of the message catalog to an XLIFF file
        """
        from DateTime import DateTime

        src_lang = self._default_language
        export_all = int(export_all)

        # Init the XLIFF handler
        xliff = XLFFile()
        # Add the translation units
        original = '/%s' % self.absolute_url(1)
        for prop in self._local_properties.keys():
            target, fuzzy = self.get_localproperty(prop, dst_lang)
            msgkey, fuzzy = self.get_localproperty(prop, src_lang)
            # If 'export_all' is true export all messages, otherwise export
            # only untranslated messages
            if export_all or not target:
                unit = xliff.add_unit(original, msgkey, None)
                unit.attributes['id'] = md5text(msgkey)
                if target:
                    unit.target = target

        # Set the file attributes
        file = xliff.files[original]
        attributes = file.attributes
        attributes['original'] = original
        attributes['product-name'] = u'Localizer'
        attributes['product-version'] = u'1.1.x'
        attributes['data-type'] = u'plaintext'
        attributes['source-language'] = src_lang
        attributes['target-language'] = dst_lang
        attributes['date'] = DateTime().HTML4()

        # Serialize
        xliff = xliff.to_str()
        # Set response headers
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        filename = '%s_%s_%s.xlf' % (self.id, src_lang, dst_lang)
        RESPONSE.setHeader('Content-Disposition',
           'attachment; filename="%s"' % filename)
        # Ok
        return xliff


    security.declareProtected('Manage messages', 'xliff_import')
    def xliff_import(self, file, REQUEST=None):
        """ XLIFF is the XML Localization Interchange File Format
            designed by a group of software providers.
            It is specified by www.oasis-open.org
        """
        try:
            data = file.read()
            xliff = XLFFile(string=data)
        except:
            return MessageDialog(title = 'Parse error',
                                 message = _('impossible to parse the file') ,
                                 action = 'manage_import',)

        num_trans = 0
        (file_ids, sources, targets) = xliff.get_languages()

        # update languages
        if len(sources) > 1 or sources[0] != self._default_language:
            return MessageDialog(title = 'Language error',
                                 message = _('incompatible language sources') ,
                                 action = 'manage_import',)
        for lang in targets:
            if lang != self._default_language and lang not in self._languages:
                self._languages += (lang,)

        # get messages
        for file in xliff.files:
            cur_target = file.attributes.get('target-language', '')
            for msg in file.body.keys():
                for (prop, val) in self._local_properties.items():
                    if val[self._default_language][0] == msg:
                        if cur_target and file.body[msg].target:
                            texte = file.body[msg].target
                            self.set_localpropvalue(prop, cur_target, texte)
                            num_trans += 1

        if REQUEST is not None:
            return MessageDialog(
                title = _(u'Messages imported'),
                message = (_(u'Imported %d messages to %s') %
                           (num_trans, ' '.join(targets))),
                action = 'manage_localPropertiesForm')


InitializeClass(LocalContent)
