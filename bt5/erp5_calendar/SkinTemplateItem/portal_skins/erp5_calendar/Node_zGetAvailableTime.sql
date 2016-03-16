<dtml-comment>
Calculate the exact time available between 2 dates.
First, sort all stock rows by ascending start date.
Then, walk through them, and increase or not the result, depending on the current and previous rows.

If a row has a negative value, the result is not increased.
If a row has a positive value, the result is increased, if:
  - no other intersecting positive interval had already been added,
  - it does not intersect with a negative interval.

Don't hesitate to draw this on a paper in order to debug this query.
</dtml-comment>

SET @result := 0,
    @current_start_date := <dtml-sqlvar expr="from_date" type="datetime">,
    @current_stop_date := <dtml-sqlvar expr="from_date" type="datetime">,
    @countable := -1,
    @total_quantity := 0;
<dtml-var sql_delimiter>

SELECT 
  @total_quantity AS total_quantity,

  <dtml-sqlvar expr="from_date" type="datetime"> AS from_date,
  <dtml-sqlvar expr="to_date" type="datetime"> AS to_date
FROM (

SELECT
  @date := GREATEST(date, <dtml-sqlvar expr="from_date" type="datetime">) AS current_c_date,
  @mirror_date := LEAST(<dtml-sqlvar expr="to_date" type="datetime">, mirror_date) AS current_mirror_date,
  
  @next_countable :=
    IF(@date >= @current_stop_date,
       quantity,
       IF((@mirror_date >= @current_stop_date) AND (quantity * @countable < 0),
          quantity,
          @countable
       )) AS next_countable, 

  @next_start_date :=
    IF(@date >= @current_stop_date,
       @date,
       IF(quantity * @countable < 0, 
          IF(@countable > 0,
             @mirror_date,
             @current_stop_date),
          @current_start_date)) AS next_start_date,

  @next_stop_date :=
    IF((@date >= @current_stop_date) OR (@mirror_date >= @current_stop_date),
       @mirror_date,
       @current_stop_date) AS next_stop_date,

  @result :=
    IF((@date < @current_start_date) OR (@countable <= 0),
       @result,
       IF(@date >= @current_stop_date,
         @result + TIME_TO_SEC(TIMEDIFF(@current_stop_date, @current_start_date)),
         @result + TIME_TO_SEC(TIMEDIFF(@date, @current_start_date)))) AS result,

  @countable := @next_countable AS countable,
  @total_quantity := IF(quantity < 0,
    @total_quantity - TIME_TO_SEC(TIMEDIFF(@mirror_date, @date)),
    @total_quantity + TIME_TO_SEC(TIMEDIFF(@mirror_date, @date))) AS total_quantity,
  @current_start_date := @next_start_date AS current_start_date,
  @current_stop_date := @next_stop_date AS current_stop_date
FROM
  stock
WHERE
  (date < <dtml-sqlvar expr="to_date" type="datetime">)
AND
  (mirror_date >= <dtml-sqlvar expr="from_date" type="datetime">)
AND
  node_uid in (
    <dtml-in node>
      <dtml-sqlvar sequence-item type="int">
      <dtml-unless sequence-end>, </dtml-unless>
    </dtml-in node> )

AND is_accountable = 1
<dtml-if resource>
  AND
  resource_uid in (
    <dtml-in resource>
      <dtml-sqlvar sequence-item type="int">
      <dtml-unless sequence-end>, </dtml-unless>
    </dtml-in resource> )
</dtml-if>

<dtml-if simulation_state>
  AND
  simulation_state in (
    <dtml-in simulation_state>
      <dtml-sqlvar sequence-item type="string">
      <dtml-unless sequence-end>, </dtml-unless>
    </dtml-in simulation_state> )
</dtml-if>

AND
  portal_type in (
    <dtml-in portal_type>
      <dtml-sqlvar sequence-item type="string">
      <dtml-unless sequence-end>, </dtml-unless>
    </dtml-in portal_type>)
ORDER BY date ASC, mirror_date ASC) AS calculated_result LIMIT 1