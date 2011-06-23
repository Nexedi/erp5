#########################################################################
# This code is taken from Products.DCWorkflowGraph-0.4-py2.6.egg
# http://pypi.python.org/pypi/Products.DCWorkflowGraph
# Author: panjunyong (panjy at zopen.cn, from ZOpen) <panjy at zopen cn>
# License: ZPL 
# The license term should be this one: http://www.zope.org/Resources/ZPL
#########################################################################

try:
    from Products.DCWorkflowGraph import DCWorkflowGraph
    from Products.DCWorkflowGraph.DCWorkflowGraph import (
        getPOT, mktemp, os, bin_search, DOT_EXE)
except ImportError:
    DCWorkflowGraph = None

if DCWorkflowGraph is not None:
    def getGraph(self, wf_id="", format="gif", REQUEST=None):
        """show a workflow as a graph, copy from:
    "OpenFlowEditor":http://www.openflow.it/wwwopenflow/Download/OpenFlowEditor_0_4.tgz
        """
        pot = getPOT(self, wf_id, REQUEST)
        encoding = 'utf-8' #### PATCHED
        pot = pot.encode(encoding)
        infile = mktemp('.dot')
        f = open(infile, 'w')
        f.write(pot)
        f.close()

        if REQUEST is None:
            REQUEST = self.REQUEST
        response = REQUEST.RESPONSE

        if format != 'dot':
            outfile = mktemp('.%s' % format)
            os.system('%s -T%s -o %s %s' % (bin_search(DOT_EXE), format, outfile, infile))
            out = open(outfile, 'rb')
            result = out.read()
            out.close()
            os.remove(outfile)
            response.setHeader('Content-Type', 'image/%s' % format)
        else:
            result = open(infile, 'r').read()
            filename = wf_id or self.getId()
            response.setHeader('Content-Type', 'text/x-graphviz')
            response.setHeader('Content-Disposition',
                               'attachment; filename=%s.dot' % filename)

        os.remove(infile)
        return result
    from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
    DCWorkflowDefinition.getGraph = getGraph
