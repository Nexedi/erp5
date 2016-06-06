<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Use_Database_Methods_Permission</string> </key>
            <value>
              <list>
                <string>Member</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>allow_simple_one_argument_traversal</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>from_date\r\n
to_date\r\n
node:list\r\n
resource:list\r\n
portal_type:list\r\n
simulation_state:list</string> </value>
        </item>
        <item>
            <key> <string>cache_time_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>class_file_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>class_name_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_hook</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Node_zGetAvailableTime</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-comment>\n
Calculate the exact time available between 2 dates.\n
First, sort all stock rows by ascending start date.\n
Then, walk through them, and increase or not the result, depending on the current and previous rows.\n
\n
If a row has a negative value, the result is not increased.\n
If a row has a positive value, the result is increased, if:\n
  - no other intersecting positive interval had already been added,\n
  - it does not intersect with a negative interval.\n
\n
Don\'t hesitate to draw this on a paper in order to debug this query.\n
</dtml-comment>\n
\n
SET @result := 0,\n
    @current_start_date := <dtml-sqlvar expr="from_date" type="datetime">,\n
    @current_stop_date := <dtml-sqlvar expr="from_date" type="datetime">,\n
    @countable := -1,\n
    @total_quantity := 0;\n
<dtml-var sql_delimiter>\n
\n
SELECT \n
  @total_quantity AS total_quantity,\n
\n
  <dtml-sqlvar expr="from_date" type="datetime"> AS from_date,\n
  <dtml-sqlvar expr="to_date" type="datetime"> AS to_date\n
FROM (\n
\n
SELECT\n
  @date := GREATEST(date, <dtml-sqlvar expr="from_date" type="datetime">) AS current_c_date,\n
  @mirror_date := LEAST(<dtml-sqlvar expr="to_date" type="datetime">, mirror_date) AS current_mirror_date,\n
  \n
  @next_countable :=\n
    IF(@date >= @current_stop_date,\n
       quantity,\n
       IF((@mirror_date >= @current_stop_date) AND (quantity * @countable < 0),\n
          quantity,\n
          @countable\n
       )) AS next_countable, \n
\n
  @next_start_date :=\n
    IF(@date >= @current_stop_date,\n
       @date,\n
       IF(quantity * @countable < 0, \n
          IF(@countable > 0,\n
             @mirror_date,\n
             @current_stop_date),\n
          @current_start_date)) AS next_start_date,\n
\n
  @next_stop_date :=\n
    IF((@date >= @current_stop_date) OR (@mirror_date >= @current_stop_date),\n
       @mirror_date,\n
       @current_stop_date) AS next_stop_date,\n
\n
  @result :=\n
    IF((@date < @current_start_date) OR (@countable <= 0),\n
       @result,\n
       IF(@date >= @current_stop_date,\n
         @result + TIME_TO_SEC(TIMEDIFF(@current_stop_date, @current_start_date)),\n
         @result + TIME_TO_SEC(TIMEDIFF(@date, @current_start_date)))) AS result,\n
\n
  @countable := @next_countable AS countable,\n
  @total_quantity := IF(quantity < 0,\n
    @total_quantity - TIME_TO_SEC(TIMEDIFF(@mirror_date, @date)),\n
    @total_quantity + TIME_TO_SEC(TIMEDIFF(@mirror_date, @date))) AS total_quantity,\n
  @current_start_date := @next_start_date AS current_start_date,\n
  @current_stop_date := @next_stop_date AS current_stop_date\n
FROM\n
  stock\n
WHERE\n
  (date < <dtml-sqlvar expr="to_date" type="datetime">)\n
AND\n
  (mirror_date >= <dtml-sqlvar expr="from_date" type="datetime">)\n
AND\n
  node_uid in (\n
    <dtml-in node>\n
      <dtml-sqlvar sequence-item type="int">\n
      <dtml-unless sequence-end>, </dtml-unless>\n
    </dtml-in node> )\n
\n
AND is_accountable = 1\n
<dtml-if resource>\n
  AND\n
  resource_uid in (\n
    <dtml-in resource>\n
      <dtml-sqlvar sequence-item type="int">\n
      <dtml-unless sequence-end>, </dtml-unless>\n
    </dtml-in resource> )\n
</dtml-if>\n
\n
<dtml-if simulation_state>\n
  AND\n
  simulation_state in (\n
    <dtml-in simulation_state>\n
      <dtml-sqlvar sequence-item type="string">\n
      <dtml-unless sequence-end>, </dtml-unless>\n
    </dtml-in simulation_state> )\n
</dtml-if>\n
\n
AND\n
  portal_type in (\n
    <dtml-in portal_type>\n
      <dtml-sqlvar sequence-item type="string">\n
      <dtml-unless sequence-end>, </dtml-unless>\n
    </dtml-in portal_type>)\n
ORDER BY date ASC, mirror_date ASC) AS calculated_result LIMIT 1

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
