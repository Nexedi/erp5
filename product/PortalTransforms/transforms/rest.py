# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from docutils.core import publish_parts
from zope.interface import implementer

import six


@implementer(ITransform)
class rest(object):
    r"""Converts from reST to HTML.

      >>> transform = rest()
      >>> class D:
      ...     def setData(self, data):
      ...         self.value = data

      >>> data = transform.convert('*hello world*', D())
      >>> print(data.value)
      <p><em>hello world</em></p>
      <BLANKLINE>

    We want the 'raw' and 'include' directives to be disabled by
    default:

      >>> try:
      ...     out = transform.convert('.. raw:: html\n  :file: <isonum.txt>', D())  # noqa
      ... except NotImplementedError:
      ...     print('Good')
      ... else:
      ...     if "&quot;raw&quot; directive disabled." in out.value:
      ...         print('Good')
      ...     else:
      ...         print('Failure')
      Good

      >>> try:
      ...     out = transform.convert('.. include:: <isonum.txt>', D())
      ... except NotImplementedError:
      ...     print('Good')
      ... else:
      ...     if "&quot;include&quot; directive disabled." in out.value:
      ...         print('Good')
      ...     else:
      ...         print('Failure')
      Good
    """

    __name__ = "rest_to_html"
    inputs = ("text/x-rst", "text/restructured",)
    output = "text/html"

    def __init__(self, name=None, **kwargs):
        if name:
            self.__name__ = name

        self.config = {
            'inputs': self.inputs,
            'output': self.output,
            'report_level': 2,
            'initial_header_level': 2,
        }

        self.config_metadata = {
            'inputs':
                ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'initial_header_level':
                ('int', 'Initial Header Level',
                 'Level of first header tag. Setting it to "2" will make '
                 'the first header be "<h2>".'),
            'report_level':
                ('int', 'Report Level',
                 'Level of error reporting. Set to "1" will display all '
                 'messages. Setting it to "5" will display no messages.'),
        }

        self.config.update(kwargs)

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        # do the format
        writer_name = kwargs.get('writer_name', 'html4css1')

        encoding = kwargs.get('encoding', 'utf-8')
        input_encoding = kwargs.get('input_encoding', encoding)
        output_encoding = kwargs.get('output_encoding', encoding)
        language = kwargs.get('language', 'en')
        initial_header_level = int(self.config.get('initial_header_level', 2))
        report_level = int(self.config.get('report_level', 2))
        # Note: we must NOT use warning_stream and stylesheet, because an attacker can abuse them.
        # See https://sourceforge.net/p/docutils/bugs/413/
        # Part of PloneHotfix20210518.
        # It would be okay if we can be sure this method is called from trusted Python code,
        # but we cannot be sure.
        # We keep them in the settings, to be sure nothing changes due to this fix.
        settings = {
            'documentclass': '',
            'traceback': 1,
            'input_encoding': input_encoding,
            'output_encoding': output_encoding,
            'stylesheet': None,
            'stylesheet_path': None,
            'file_insertion_enabled': 0,
            'raw_enabled': 0,
            'language_code': language,
            # starting level for <H> elements:
            'initial_header_level': initial_header_level + 1,
            # set the reporting level to something sane:
            'report_level': report_level,
            # don't break if we get errors:
            'halt_level': 6,
            # remember warnings:
            'warning_stream': None
        }

        parts = publish_parts(
            source=orig,
            writer_name=writer_name,
            settings_overrides=settings,
            config_section='zope application'
        )

        header = '<h%(level)s class="title">%(title)s</h%(level)s>\n' % {
            'level': initial_header_level,
            'title': parts['title']}

        subheader = '<h%(level)s class="subtitle">%(subtitle)s</h%(level)s>\n' % {  # noqa
            'level': initial_header_level+1,
            'subtitle': parts['subtitle']}

        body = '%(docinfo)s%(body)s' % {
            'docinfo': parts['docinfo'],
            'body': parts['body']}

        html = ''
        if parts['title']:
            html = html + header
        if parts['subtitle']:
            html = html + subheader
        html = html + body

        # TODO: check if this unicode condition works on Python 3.
        if six.PY2 and output_encoding != 'unicode':
            html = html.encode(output_encoding)

        html = html.replace(' class="document"', '', 1)
        data.setData(html)
        return data


def register():
    return rest()
