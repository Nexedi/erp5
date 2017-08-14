# -*- coding: utf-8 -*-

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zExceptions import Unauthorized
import transaction

class ClusterDataNotebookMixin(object):
  def setupPreference(self):
    self.preference = self.portal.portal_preferences.newContent(
      portal_type='System Preference',
      title=self.id(),
      priority=1,
      preferred_cluster_data_notebook_enabled=True
    )
    self.preference.enable()
    self.tic()

  def disablePreference(self):
    self.preference.disable()
    self.tic()

  def afterSetUp(self):
    self.setupPreference()
    # Create user to be used in tests
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser('dev_user', '', ['Manager',], [])
    self.tic()
    self.login('dev_user')

  def beforeTearDown(self):
    self.disablePreference()

  def newNotebook(self):
    return self.portal.cluster_data_notebook_module.newContent(
        portal_type='Cluster Data Notebook')

  def executeCell(self, notebook, code):
    cluster_data_notebook_line_url = notebook.ClusterDataNotebook_postExecution(code)
    cluster_data_notebook_line = self.portal.restrictedTraverse(cluster_data_notebook_line_url)
    self.tic()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    return cluster_data_notebook_line.getResult()

class TestClusterDataNotebook(ClusterDataNotebookMixin, ERP5TypeTestCase):
  def test_ClusterDataNotebook_postExecution(self):
    code = 'return "tested"'
    cluster_data_notebook = self.portal.cluster_data_notebook_module.newContent(
      portal_type='Cluster Data Notebook')

    cluster_data_notebook_line_url = cluster_data_notebook.ClusterDataNotebook_postExecution(code)
    cluster_data_notebook_line = self.portal.restrictedTraverse(cluster_data_notebook_line_url)
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    transaction.commit()
    self.assertEqual('Running', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.tic()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.assertEqual(
      'tested',
      cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebook_postExecution_disabled(self):
    self.preference.edit(preferred_cluster_data_notebook_enabled=False)
    self.tic()
    code = 'return "tested"'
    cluster_data_notebook = self.portal.cluster_data_notebook_module.newContent(
      portal_type='Cluster Data Notebook')
    self.assertRaises(Unauthorized, cluster_data_notebook.ClusterDataNotebook_postExecution, code)

class TestClusterDataNotebookLine(ClusterDataNotebookMixin, ERP5TypeTestCase):
  def newClusterDataNotebookLine(self):
    return self.portal.cluster_data_notebook_module.newContent(
      portal_type='Cluster Data Notebook').newContent(portal_type='Cluster Data Notebook Line')

  def test_code_storage(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()

    code = 'return 1'

    cluster_data_notebook_line.edit(
      default_code_body=code
    )

    self.tic()

    self.assertEqual(
      ['default_code'],
      list(cluster_data_notebook_line.objectIds())
    )

    self.assertEqual(
      code,
      cluster_data_notebook_line.getDefaultCodeBody().strip()
    )

  def test_ClusterDataNotebookLine_execute(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='return "tested"')
    cluster_data_notebook_line.ClusterDataNotebookLine_execute()
    self.assertEqual(
      'tested',
      cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_executeEmpty(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='')
    cluster_data_notebook_line.ClusterDataNotebookLine_execute()
    self.assertEqual(
      None,
      cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_execute_disabled(self):
    self.preference.edit(preferred_cluster_data_notebook_enabled=False)
    self.tic()
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='return "tested"')
    self.assertRaises(Unauthorized, cluster_data_notebook_line.ClusterDataNotebookLine_execute)

  def test_ClusterDataNotebookLine_execute_nonAllowedModule(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='import pickle')
    cluster_data_notebook_line.ClusterDataNotebookLine_execute()
    self.assertTrue(
      'Unauthorized: import of \'pickle\' is unauthorized' in cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_execute_withException(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='raise ValueError("Stored value error")')
    cluster_data_notebook_line.ClusterDataNotebookLine_execute()
    self.assertTrue(
      'ValueError: Stored value error' in cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_execute_withSyntaxError(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='ret urn "Stored problem"')
    cluster_data_notebook_line.ClusterDataNotebookLine_execute()
    self.assertTrue(
      'RuntimeError: ERP5 Cluster Data Script default_code has errors.' in cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_postExecution_disabled(self):
    self.preference.edit(preferred_cluster_data_notebook_enabled=False)
    self.tic()
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='return "tested"')
    self.assertRaises(Unauthorized, cluster_data_notebook_line.ClusterDataNotebookLine_postExecution)

  def test_ClusterDataNotebookLine_postExecution(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='return "tested"')
    cluster_data_notebook_line.ClusterDataNotebookLine_postExecution()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    transaction.commit()
    self.assertEqual(
      None,
      cluster_data_notebook_line.getResult()
    )
    self.assertEqual('Running', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.tic()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.assertEqual(
      'tested',
      cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_postExecution_withException(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='raise ValueError("Stored value error")')
    cluster_data_notebook_line.ClusterDataNotebookLine_postExecution()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    transaction.commit()
    self.assertEqual(
      None,
      cluster_data_notebook_line.getResult()
    )
    self.assertEqual('Running', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.tic()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.assertTrue(
      "ValueError: Stored value error" in cluster_data_notebook_line.getResult()
    )

  def test_ClusterDataNotebookLine_postExecution_withSyntaxError(self):
    cluster_data_notebook_line = self.newClusterDataNotebookLine()
    cluster_data_notebook_line.edit(default_code_body='ret urn "Stored problem"')
    cluster_data_notebook_line.ClusterDataNotebookLine_postExecution()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    transaction.commit()
    self.assertEqual(
      None,
      cluster_data_notebook_line.getResult()
    )
    self.assertEqual('Running', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.tic()
    self.assertEqual('Ready', cluster_data_notebook_line.ClusterDataNotebookLine_getState())
    self.assertTrue(
      "RuntimeError: ERP5 Cluster Data Script default_code has errors." in cluster_data_notebook_line.getResult()
    )


class TestClusterDataNotebookPostExecution(ClusterDataNotebookMixin, ERP5TypeTestCase):
  """Top level tests for asserting that code is called as expected"""
  def testVariablesBetweenCells(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
some_int = 1
some_string = "string"

print some_int
print some_string
return printed
""")
    self.assertEqual(
      result,
      "1\nstring\n")

    # Prove that variables from previous cell are available
    result = self.executeCell(notebook, """
print some_int
print some_string
return printed
""")

    self.assertEqual(
      result,
      "1\nstring\n"
    )

  def testImportModule(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
import pprint
print pprint.pformat('1')
return printed
""")
    self.assertEqual(
      result,
      "'1'\n")

    # Prove that variables from previous cell are available
    result = self.executeCell(notebook, """
print pprint.pformat('1')
return printed
""")

    self.assertEqual(
      result,
      "'1'\n"
    )

  def testImportModuleAs(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
import pprint as pp
print pp.pformat('1')
return printed
""")
    self.assertEqual(
      result,
      "'1'\n")

    # Prove that variables from previous cell are available
    result = self.executeCell(notebook, """
print pp.pformat('1')
return printed
""")

    self.assertEqual(
      result,
      "'1'\n"
    )

  def testImportModuleFrom(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
from pprint import pformat
print pformat('1')
return printed
""")
    self.assertEqual(
      result,
      "'1'\n")

    # Prove that variables from previous cell are available
    result = self.executeCell(notebook, """
print pformat('1')
return printed
""")

    self.assertEqual(
      result,
      "'1'\n"
    )

  def testVariable_context(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
print context.getParentValue().getRelativeUrl()
return printed
""")
    self.assertEqual(
      result,
      "%s\n" % (notebook.getRelativeUrl(),))

  def testVariable_script(self):
    notebook = self.newNotebook()

    # Prove that directly using variables works
    result = self.executeCell(notebook, """
print script.id
return printed
""")
    self.assertEqual(
      result,
      "default_code\n")

  def test_returnLast(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
a = 1
a
""")
    self.assertEqual(result, "1")

  def test_delWorks(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
a = 1
return a
""")
    self.assertEqual(result, "1")

    result = self.executeCell(notebook, """
print a ; return printed
#del a""")
    self.assertEqual(result, "1\n")

    result = self.executeCell(notebook, """
del a
""")
    self.assertEqual(result, None)

    result = self.executeCell(notebook, """
return a
""")
    self.assertEqual(result, "check")

    self.assertTrue(
      'UnboundLocalError: local variable \'a\' referenced before assignment' in result,
      result)

  def test_exceptionDoesNotResetVariables(self):
    notebook = self.newNotebook()

    result = self.executeCell(notebook, """
a = 1
return a
""")
    self.assertEqual(
      result,
      "1")

    result = self.executeCell(notebook, """
raise ValueError
""")

    self.assertTrue(
      "ValueError" in result,
      result)

    result = self.executeCell(notebook, """
return a
""")
    self.assertEqual(
      result,
      "1")

  def test_variablesMerged(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
a = 1
return a
    """)
    self.assertEqual(
      result,
      "1")

    result = self.executeCell(notebook, """
b = 2
return b
    """)
    self.assertEqual(
      result,
      "2")

    result = self.executeCell(notebook, """
return (a, b)
    """)
    self.assertEqual(
      result,
      "(1, 2)")

  def testPandasDataFrame(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas as pd
dataframe = pd.DataFrame({
  'dates' : pd.date_range('20130101', periods=6)
})
return dataframe[['dates']]
    """)
    self.assertEqual(
      result,
      """       dates
0 2013-01-01
1 2013-01-02
2 2013-01-03
3 2013-01-04
4 2013-01-05
5 2013-01-06""")

  def testNumpySum(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import numpy
return numpy.sum([1,2,3])
    """)
    self.assertEqual(
      result,
      "6")

  def testPandasDatetimeProperties(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas as pd
dataframe = pd.DataFrame({
  'dates' : pd.date_range('20130101', periods=6)
})
return dataframe['dates'].dt.month
""")
    self.assertEqual(
      result,
      """0    1
1    1
2    1
3    1
4    1
5    1
Name: dates, dtype: int64""")

  def testNumpyRandomRandn(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
# import numpy  # <-- this is not enough, some kind of side effect while import numpy.random is called
#               #     which result in access to numpy.random.randn
import numpy.random
numpy.random.randn(6,4)
    """)
    self.assertEqual(
      result,
      None)

  def testPandasDateRange(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas
return pandas.date_range('20130101', periods=6)
    """)
    self.assertEqual(
      result,
      """DatetimeIndex(['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
               '2013-01-05', '2013-01-06'],
              dtype='datetime64[ns]', freq='D')""")

  def testPandasSeries(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas as pd

rng = pd.date_range('1/1/2012', periods=5, freq='S')
ts = pd.Series([9,8,7,6,5], index=rng)
return ts.resample('5Min').sum()
""")
    self.assertEqual(
      result,
      "2012-01-01    35\nFreq: 5T, dtype: int64")

  def testPandasStringMethods(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas as pd
df = pd.DataFrame({
  'idx': pd.Series(1,index=list(range(1)),dtype='float32'),
  'text': 'some/nice/text'
})
return df['text'].str.split('/', expand=True)
""")
    self.assertEqual(
      result,
      '      0     1     2\n0  some  nice  text')

  def testPandasDataFrameGroupBy(self):
    notebook = self.newNotebook()
    result = self.executeCell(notebook, """
import pandas as pd
df = pd.DataFrame({
  'idx': pd.Series(1,index=list(range(1)),dtype='float32'),
  'text': 'some/nice/text'
})
return df.groupby(['text']).agg({'idx': lambda x: x.sum()})
    """)
    self.assertEqual(
      result,
      "                idx\ntext               \nsome/nice/text  1.0")

  def testExternalModule(self):
    def checkModule(module):
      if self.executeCell(self.newNotebook(), 'import %s as _' % module) is None:
        return True
      else:
        return False

    module_list = [
      'datetime',
      'h5py',
      'math',
      'matplotlib',
      'matplotlib.pyplot',
      'numpy',
      'numpy.random',
      'openpyxl',
      'pandas',
      'pylab',
      'scipy',
      'seaborn',
      'sklearn',
      'statsmodels',
      'sympy',
      'xlrd',
    ]
    imported_module_list = [module for module in module_list if checkModule(module)]
    self.assertEqual(
      set(module_list),
      set(imported_module_list),
      'Missing modules: %s' % ' '.join(set(module_list)-set(imported_module_list)))

class TestClusterDataNotebookScenarios(ClusterDataNotebookMixin, ERP5TypeTestCase):
  def test_10_minutes_to_pandas(self):
    # Checks the most important aspects of https://pandas.pydata.org/pandas-docs/stable/10min.html
    notebook = self.newNotebook()
    def executeCell(code):
      return self.executeCell(notebook, code)

    def executeAssertNone(code):
      result = executeCell(code)
      self.assertEqual(None, result)

    executeAssertNone('import pandas as pd')
    executeAssertNone('import numpy as np')
    executeAssertNone('import matplotlib.pyplot as plt')

    executeAssertNone('s = pd.Series([1,3,5,np.nan,6,8])')
    result = executeCell('return s')  # XXX: shall be without return
    self.assertEqual(
      result,
      """0    1.0
1    3.0
2    5.0
3    NaN
4    6.0
5    8.0
dtype: float64""")

    executeAssertNone("dates = pd.date_range('20130101', periods=6)")
    result = executeCell('return dates')  # XXX: shall be without return
    self.assertEqual(
      result,
      """DatetimeIndex(['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
               '2013-01-05', '2013-01-06'],
              dtype='datetime64[ns]', freq='D')""")

    executeAssertNone("""
df = pd.DataFrame(
  [
    [1, 2, 3, 4],
    [17, 18, 19, 20],
    [9, 10, 11, 12],
    [13, 14, 15, 16],
    [21, 22, 23, 24],
    [5, 6, 7, 8],
  ], index=dates, columns=list('ABCD'))""")
    result = executeCell("return df")
    self.assertEqual(result, """             A   B   C   D
2013-01-01   1   2   3   4
2013-01-02  17  18  19  20
2013-01-03   9  10  11  12
2013-01-04  13  14  15  16
2013-01-05  21  22  23  24
2013-01-06   5   6   7   8""")

    executeAssertNone("""
df2 = pd.DataFrame({ 'A' : 1.,
                     'B' : pd.Timestamp('20130102'),
                     'C' : pd.Series(1,index=list(range(4)),dtype='float32'),
                     'D' : np.array([3] * 4,dtype='int32'),
                     'E' : pd.Categorical(["test","train","test","train"]),
                     'F' : 'foo' })""")

    result = executeCell("return df2")
    self.assertEqual(
      result,
      """     A          B    C  D      E    F
0  1.0 2013-01-02  1.0  3   test  foo
1  1.0 2013-01-02  1.0  3  train  foo
2  1.0 2013-01-02  1.0  3   test  foo
3  1.0 2013-01-02  1.0  3  train  foo""")
    result = executeCell("return df2.dtypes")
    self.assertEqual(
      result, """\
A           float64
B    datetime64[ns]
C           float32
D             int32
E          category
F            object
dtype: object"""
    )

    result = executeCell("return df.head()")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-01   1   2   3   4
2013-01-02  17  18  19  20
2013-01-03   9  10  11  12
2013-01-04  13  14  15  16
2013-01-05  21  22  23  24""")

    result = executeCell("return df.tail(3)")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-04  13  14  15  16
2013-01-05  21  22  23  24
2013-01-06   5   6   7   8""")

    result = executeCell("return df.index")
    self.assertEqual(
      result,
      """DatetimeIndex(['2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04',
               '2013-01-05', '2013-01-06'],
              dtype='datetime64[ns]', freq='D')"""
    )

    result = executeCell("return df.columns")
    self.assertEqual(
      result,
      """Index([u'A', u'B', u'C', u'D'], dtype='object')""")

    result = executeCell("return df.values")
    self.assertEqual(result, """\
[[ 1  2  3  4]
 [17 18 19 20]
 [ 9 10 11 12]
 [13 14 15 16]
 [21 22 23 24]
 [ 5  6  7  8]]""")

    result = executeCell("return df.describe()")
    self.assertEqual(result, """\
               A          B          C          D
count   6.000000   6.000000   6.000000   6.000000
mean   11.000000  12.000000  13.000000  14.000000
std     7.483315   7.483315   7.483315   7.483315
min     1.000000   2.000000   3.000000   4.000000
25%     6.000000   7.000000   8.000000   9.000000
50%    11.000000  12.000000  13.000000  14.000000
75%    16.000000  17.000000  18.000000  19.000000
max    21.000000  22.000000  23.000000  24.000000""")

    result = executeCell("return df.T")
    self.assertEqual(result, """\
   2013-01-01  2013-01-02  2013-01-03  2013-01-04  2013-01-05  2013-01-06
A           1          17           9          13          21           5
B           2          18          10          14          22           6
C           3          19          11          15          23           7
D           4          20          12          16          24           8""")

    result = executeCell("return df.sort_index(axis=1, ascending=False)")
    self.assertEqual(result, """\
             D   C   B   A
2013-01-01   4   3   2   1
2013-01-02  20  19  18  17
2013-01-03  12  11  10   9
2013-01-04  16  15  14  13
2013-01-05  24  23  22  21
2013-01-06   8   7   6   5""")

    result = executeCell("return df.sort_values(by='B')")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-01   1   2   3   4
2013-01-06   5   6   7   8
2013-01-03   9  10  11  12
2013-01-04  13  14  15  16
2013-01-02  17  18  19  20
2013-01-05  21  22  23  24""")

    result = executeCell("return df['A']")
    self.assertEqual(result, """\
2013-01-01     1
2013-01-02    17
2013-01-03     9
2013-01-04    13
2013-01-05    21
2013-01-06     5
Freq: D, Name: A, dtype: int64""")

    result = executeCell("return df[0:3]")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-01   1   2   3   4
2013-01-02  17  18  19  20
2013-01-03   9  10  11  12""")

    result = executeCell("return df['20130102':'20130104']")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-02  17  18  19  20
2013-01-03   9  10  11  12
2013-01-04  13  14  15  16""")

    result = executeCell("return df.loc['20130102':'20130104',['A','B']]")
    self.assertEqual(result, """\
             A   B
2013-01-02  17  18
2013-01-03   9  10
2013-01-04  13  14""")

    result = executeCell("return df[df.A > 6]")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-02  17  18  19  20
2013-01-03   9  10  11  12
2013-01-04  13  14  15  16
2013-01-05  21  22  23  24""")

    result = executeCell("return df.apply(np.cumsum)")
    self.assertEqual(result, """\
             A   B   C   D
2013-01-01   1   2   3   4
2013-01-02  18  20  22  24
2013-01-03  27  30  33  36
2013-01-04  40  44  48  52
2013-01-05  61  66  71  76
2013-01-06  66  72  78  84""")

    result = executeCell("return df.groupby('A').sum()")
    self.assertEqual(result, """\
     B   C   D
A             
1    2   3   4
5    6   7   8
9   10  11  12
13  14  15  16
17  18  19  20
21  22  23  24""")

    result = executeCell("return pd.pivot_table(df, values='D', index=['A', 'B'], columns=['C'])")
    self.assertEqual(result, """\
C       3    7     11    15    19    23
A  B                                   
1  2   4.0  NaN   NaN   NaN   NaN   NaN
5  6   NaN  8.0   NaN   NaN   NaN   NaN
9  10  NaN  NaN  12.0   NaN   NaN   NaN
13 14  NaN  NaN   NaN  16.0   NaN   NaN
17 18  NaN  NaN   NaN   NaN  20.0   NaN
21 22  NaN  NaN   NaN   NaN   NaN  24.0""")