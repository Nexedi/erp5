# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 panjunyong (panjy at zopen.cn, from ZOpen)
#                    Nexedi SARL and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

def getObjectTitle(obj, REQUEST=None):
  """
  Get a state/transition title to be displayed in the graph.

  Monkey-patched to support translation similar to what
  Products.ERP5Type.Accessor.WorkflowState.TranslatedGetter does
  """
  if REQUEST is not None:
    only_ids = REQUEST.get('only_ids', False)
    translate = REQUEST.get('translate', False)
  else:
    only_ids = False
    translate = False

  _id = obj.getId()
  title = obj.title
  if not title or only_ids:
    title = _id
  else:
    if translate:
      # Translate the title in all supported Localizer languages
      wf_id = obj.getWorkflow().id
      localizer = obj.Localizer
      original_title = title
      for lang in localizer.get_supported_languages():
        msg_id = '%s [state in %s]' % (title, wf_id)
        translated_title = localizer.erp5_ui.gettext(
          msg_id,
          lang=lang,
          # Fallback on non-workflow state translation
          default=localizer.erp5_ui.gettext(original_title,
                                            lang=lang,
                                            default=None))

        if (translated_title is not None and
            translated_title != original_title):

          title += "\\n%s" % translated_title

    title += "\\n(%s)"% _id

  return title

from Products.DCWorkflowGraph import DCWorkflowGraph
DCWorkflowGraph.getObjectTitle = getObjectTitle

from Products.DCWorkflowGraph.config import bin_search_path, DOT_EXE
from tempfile import NamedTemporaryFile
from zLOG import LOG, WARNING

def getGraph(self, wf_id="", format="png", REQUEST=None):
  """show a workflow as a graph, copy from:
"OpenFlowEditor":http://www.openflow.it/wwwopenflow/Download/OpenFlowEditor_0_4.tgz

  Monkey-patched to specify font name and size as 'dot' uses Times font by
  default which does not support Japanese:

  http://www.graphviz.org/doc/fontfaq.txt

  Another solution would be to modify fontconfig configuration so that Times
  match Japanese font or to use Unifont which supports many code points.
  """
  try:
    pot = DCWorkflowGraph.getPOT(self, wf_id, REQUEST)
  except TypeError:
    # DCWorkflowGraph < 0.4
    pot = DCWorkflowGraph.getPOT(self, wf_id)
  try:
    encoding = self.portal_properties.site_properties.getProperty(
      'default_charset', 'utf-8')
  except AttributeError:
    # no portal_properties or site_properties, fallback to:
    encoding = self.management_page_charset.lower()
  pot = pot.encode(encoding)
  result = None
  with NamedTemporaryFile(suffix='.dot') as infile:
    infile.write(pot)
    infile.seek(0)

    if REQUEST is None:
      REQUEST = self.REQUEST
    response = REQUEST.RESPONSE

    if format != 'dot':
      with NamedTemporaryFile(suffix='.%s' % format) as outfile:
        os.system('%s -Nfontname="IPAexGothic" -Nfontsize=10 '
                  '-Efontname="IPAexGothic" -Efontsize=10 -T%s '
                  '-o %s %s' % (DCWorkflowGraph.bin_search(DOT_EXE),
                                format, outfile, infile))

        result = outfile.read()

      response.setHeader('Content-Type', 'image/%s' % format)
    else:
      result = infile.read()
      filename = wf_id or self.getId()
      response.setHeader('Content-Type', 'text/x-graphviz')
      response.setHeader('Content-Disposition',
                         'attachment; filename=%s.dot' % filename)

  if not result:
    LOG("ERP5Type.patches.DCWorkflowGraph", WARNING,
        "Empty %s graph file" % format)

  return result

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
DCWorkflowDefinition.getGraph = getGraph
