##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Vincent Pelletier <vincent@nexedi.com>
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

from zope.interface import Interface

class ISearchKeyCatalog(Interface):

  def buildQuery(kw, ignore_empty_string=True, operator='and'):
    """
      Build a ComplexQuery from kw values.

      kw (dict: string keys, any value)
        A query will be emited based on its value. Depending on the type of
        the value it is handled differently. Query values will be passed
        through to result (key is ignored). For all other types, their key
        must be either a known column of a sql_search_tables table, or a
        related key name.
        - String values will be parsed according to the default SearchKey of
          their real column (even for related keys). If parsing was
          successful, Queries will be generated from its output.
          Otherwise, that value will be taken as such.
        - Dictionary values can be composed of the following keys:
          'query': Their payload value, considered as empty if not given.
          'key': The SearchKey to use for this value, overriding default
                 column configuration.
          (for other possible keys, see SearchKeys)
          They will be taken as such.
        - All other types will be taken as such, and no "empty" check will be
          performed on them.
      ignore_empty_string (boolean)
        If True, values from kw which are empty will be skipped.
        This parameter should ultimately disapear *and* be disabled by
        default, as it is bad to ignore parameters based on their value if
        that value has a meaning in SQL.
      operator (string)
        Used to explicit the logical relation between kw entries.
        It must be a valid ComplexQuery logical operator ('and', 'or').
    """

  def buildEntireQuery(kw, query_table='catalog', ignore_empty_string=1,
                       limit=None, extra_column_list=None):
    """
      Construct and return an instance of EntireQuery class from given
      parameters by calling buildQuery.

      ignore_empty_string (boolean)
        See buildQuery.
      limit (1-tuple, 2-tuple)
        If given, will emit SQL to limit the number of result lines.
      group_by_list (list of strings)
        If given, will emit SQL to group found lines on given parameter names
        (their column if they are column names, corresponding virtual columns
        otherwise - as for related keys).
      select_dict (dict, key: string, value: string, None)
        Given values describe columns to make available in SQL result.
        If column is aliased in result set, key is the alias and value is the
        column.
        Otherwise, key is the column, and value can be None or the same as
        key.
      select_list (list of strings)
        Same as providing select_dict with select_list items as keys, and None
        values.
      order_by_list (list of 1-, 2-, or 3-tuples of strings)
        If given, will emit SQL to sort result lines.
        Sort will happen with decreasing precedence in list order.
        Given n-tuples can contain those values, always in this order:
         - parameter name
         - sort order (see SQL documentation of 'ORDER BY')
         - type cast (see SQL documentation of 'CAST')
        Sort will happen on given parameter name (its column if it's a column
        name, corresponding virtual column otherwise - as for related keys).
      Extra parameters are passed through to buildQuery.

      Backward compatibility parameters:
      Those parameters are deprecated and should not be used. They are present
      to provide backward compatibility with former ZSQLCatalog version.
      REQUEST
        Ignored.
      extra_column_list (list)
      query_table (string, None)
        The table to use as catalog table.
        If given and None, no catalog table will be used. Use this when you
        are using SQLCatalog to generate manualy a part of another query.
        That table has a special position in returned query:
         - all other tables are joined on this one (when it is required to use
           other tables)
         - it is expected to have some columns (uid, path)
        It is strongly discouraged to use this parameter for any value other
        than None.
      group_by
        Use group_by_list instead.
      group_by_expression
        Use group_by_list instead.
      select_expression
        Use select_list or select_dict instead.
      sort_on
        Use order_by_list instead.
      sort_order
        Use order_by_list instead.
      from_expression
        This value will be emited in SQL directly in addition to computed
        value.
        There is no replacement.
      where_expression
        This value will be emited in SQL directly in addition to computed
        value.
        Use Query instances instead.
      select_expression_key
        This prevents given column from being ignored even if they could not
        be mapped.
        There is no replacement.
    """


  def buildSQLQuery(query_table='catalog', REQUEST=None,
                    ignore_empty_string=1, only_group_columns=False,
                    limit=None, extra_column_list=None,
                    **kw):
    """
      Return an SQLExpression-generated dictionary (see
      SQLExpression.asSQLExpressionDict). That SQLExpression is generated by
      an EntireQuery, itself generated by buildEntireQuery from given
      parameters.

      only_group_columns
        Replaces former stat__ parameter.
        Used to globally disalow use of non-group columns in SQL.

      For other parameters, see buildEntireQuery.
    """

  def getSearchKey(column, search_key=None):
    """
      Returns the default SearchKey instance for the
      requested column. There is one instance per
      search_key (incl. virtual keys surch as
      source_title) and we try to compute it once
      only and cache it.
      If search_key is provided, it is used as the
      name of the search key class to return.
    """

  def getComparisonOperator(operator):
    """
      Return a comparison operator matching given string.
      String must be a valid SQL comparison operator (=, LIKE, IN, ...).
      String case does not matter.
      There is one comparison operator instance per possible string value.
    """

  def hasColumn(column):
    """
      Check if the given column or virtual column (in case
      of related keys) exists or not
    """

  # TODO: add support for other operators (logical, ensemblist (?))

  def searchResults(REQUEST=None, **kw):
    """
      Invokes queryResults with the appropriate
      ZSQL Method to return a list of results
    """

  def countResults(REQUEST=None, **kw):
    """
      Invokes queryResults with the appropriate
      ZSQL Method to return a statistics for
      a list of results
    """

  def queryResults(sql_method, REQUEST=None, src__=0, build_sql_query_method=None, **kw):
    """
      Return the result of the given 'sql_method' ZSQL Method after
      processing all parameters to build a Query object passed to
      that method.

      The implementation should do the following.

      1- Use **kw parameters to build a Query object
         by invoking buildQuery

      2- Build a ColumnMap instance by invoking
         the buildColumnMap on the Query. Some
         optmisation may happen here to try
         to build the best possible ColumnMap and
         use the best possible indices for joining.
         During the ColumnMap build process, the
         Search Key associated to each Query node
         in the Query tree registers the columns
         which are used (ex. to search) or provided
         (ex. MATCH value for full text search,
         interleave expression or parameter in a
         UNION Query)

      3- Render the query object as an SQLExpression
         instance. This instance contains all necessary
         parts to generate:
           - where_expression
           - sort_expression
           - group_by_expression
           - select_expression

      4- Invoke sql_method
    """

  def isAdvancedSearchText(search_text):
    """
      Returns True if given value follows Search Text "advanced" syntax,
      False otherwise.
    """

  def parseSearchText(search_text, column=None, search_key=None, is_valid=None):
    """
      Parses given SearchText expression using given column's parser
      (determined by the SearchKey it is configured to use by default), or
      given SearchKey name.

      search_text (string)
        SearchText to parse.
      column (string)
        Column to use to determine which SearchKey to use for parsing.
        Either this parameter or search_key must be provided.
      search_key (string)
        Name of the SearchKey to use for parsing.
        Either this parameter or column must be provided.
      if_valid (callback)
        Callback method to use to decide wether an encountered column-ish
        identifier in SearchText is a valid column.
        If not provided, catalog schema will be used.
    """

  def isValidColumn(column_id):
    """
      Returns wether given string is a known column.
      Note: related keys and scriptable keys are considered columns.
    """
