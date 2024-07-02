<dtml-if "'WeightedAverage' in valuation_method">

/*
Almost the same SQL for WeightedAverage/MonthlyWeightedAverage
since they rely on the same kind of "split by period" model.

First split timeframe into Year (or Month) periods, and fold all movements
during each period.
Then perform a weighted average over all periods.
*/

set @total_asset_price=0.0, @total_quantity=0.0
<dtml-var sql_delimiter>
select
    byperiod.*,
    (@unit_price:=(@total_asset_price+incoming_total_price)/(@total_quantity+incoming_total_quantity)) as unit_price,
    (@total_asset_price:=
        @total_asset_price +
        incoming_total_price +
        outgoing_total_quantity * @unit_price) as total_asset_price,
    (@total_quantity:=@total_quantity+quantity_diff) as total_quantity
from
    (
        select
            month(date) as d_month,
            year(date) as d_year,
            SUM(IF(quantity>0, total_price, 0)) as incoming_total_price,
            SUM(IF(quantity>0, quantity, 0)) as incoming_total_quantity,
            SUM(IF(quantity>0, 0, quantity)) as outgoing_total_quantity,
            SUM(quantity) as quantity_diff
        from
            stock, catalog
        where
          <dtml-var where_expression>
        group by
            d_year<dtml-if "'Monthly' in valuation_method">, d_month</dtml-if>
        order by
            d_year<dtml-if "'Monthly' in valuation_method">, d_month</dtml-if>
    ) as byperiod
order by d_year<dtml-if "'Monthly' in valuation_method">, d_month</dtml-if>


<dtml-elif "'MovingAverage'==valuation_method">
/*
Very similar to (Monthly)WeightedAverage except that we do not have to
split the timeframe / fold movements and simply perform a weighted average
on all single movements.

Parameter lowest_value_test compares latest price and Moving average price and takes the
smallest one.
*/

SET @total_asset_price=0, @total_quantity=0, @latest_price=null, @running_total_asset_price=0
<dtml-var sql_delimiter>
select
    (@incoming_total_price:=IF(quantity>0, total_price, 0)) as incoming_total_price,
    @latest_price:=IF(quantity>0, total_price/quantity, @latest_price) as latest_price,

    @unit_price:=((@total_asset_price+@incoming_total_price)/(@total_quantity+GREATEST(0, quantity))) as unit_price,
    (@running_total_asset_price:=
        @running_total_asset_price +
        @incoming_total_price +
        LEAST(0, quantity) * @unit_price) as running_total_asset_price,
    (@total_quantity:=@total_quantity+quantity) as dummy,
    <dtml-if "lowest_value_test">
     (@total_asset_price:=LEAST(@running_total_asset_price, @total_quantity*@latest_price)) as total_asset_price
    <dtml-else>
     (@total_asset_price:= @running_total_asset_price) as total_asset_price
    </dtml-if>
from
   stock, catalog
where
  <dtml-var where_expression>
order by date

<dtml-elif "valuation_method=='Fifo'">

/*
FIFO inventory valuation is about finding out the price of items in
inventory that stay until t=END after transactions from t=0.
For we care only about items found in inventory at t=END, it
is interesting to notice that a few of the earliest movements can be
discarded along the way of our computation:

1)Assume that you know the @total_output_quantity during the considered
  timeframe.
2)Now notice that in this model you can fold all outgoing movements into a single
  big movement of @total_output_quantity taking place a t=END, and obtain the
  same, yet simpler to compute valuation.
3)It is then easy to see that while the sum of quantities of incoming
  movements accounts for less than @total_output_quantity, items queued in by
  these movements will be completely removed by the final outgoing movement.
  It is safe to ignore those first movements in our computation.

This means that when iterating forward over incoming movements, from t=0 to t=END,
incoming movements can be ignored until their cumulative quantity sum is larger
than the total output quantity. After this, each incoming movement will stay
forever in inventory.

Thus, each movement has a value of:
  max(0, (quantity-@unbalanced_output) * unit_price)
if @unbalanced_output is initialized to @total_output_quantity and reduced by
quantity at each step:
  unbalanced_output=max(0, unbalanced_output-quantity)

Parameter lowest_value_test compares latest price and FIFO price and takes the
smallest one.
*/
SET
 @unbalanced_output:=
   IFNULL((SELECT
      SUM(-quantity)
    FROM
      stock, catalog
    WHERE
      quantity < 0
    AND
      <dtml-var where_expression>
    ),0),
 @total_asset_price=0.0,
 @running_total_asset_price=0.0,
 @running_quantity=0.0
<dtml-var sql_delimiter>

SELECT

 (@running_quantity:=@running_quantity +
   GREATEST(0, quantity-@unbalanced_output)
 ) AS running_quantity,
 (@running_total_asset_price:=@running_total_asset_price +
   GREATEST(0, (quantity-@unbalanced_output) * IFNULL(total_price,0)/quantity)
 ) AS running_total_asset_price,
 (@unbalanced_output:=GREATEST(0, @unbalanced_output-quantity)) as dummy,
 <dtml-if "lowest_value_test">
  (@total_asset_price:=LEAST(@running_total_asset_price,
                             @running_quantity * total_price/quantity)) as total_asset_price
 <dtml-else>
  (@total_asset_price:= @running_total_asset_price) as total_asset_price
 </dtml-if>

FROM
 stock, catalog
WHERE
  quantity > 0
AND
  <dtml-var where_expression>
order by date

<dtml-elif "valuation_method=='Filo'">


/*
What matters for FILO inventory value is the amount that never goes out of inventory
and stays in at the bottom of the pile until t=END:
If, for each incoming movement, we are able to tell how many items of this movement
are taken out of inventory in future, then we are finished: the remaining quantity
of this movement will be found in the final inventory and should be counted in the
valuation.

To know the future/destiny of each incoming movement, the easier way is to
iterate movements in a backwards fashion, from latest (t=END) to earliest (t=0),
and remember how many items are removed from the inventory by outgoing movements.

We sum in @unbalanced_output the (absolute) sum of outgoing movements quantities
until we reach an incoming movement. Then:
 - if incoming_movement.quantity > @unbalanced_output, we know for sure that
   (quantity-@unbalanced_output) WILL remain in the inventory at t=END. We can thus
   add (quantity-@unbalanced_output)*unit_price to asset_price, and reset
   @unbalanced_output to zero.
 - if incoming_movement.quantity <= @unbalanced_output then all of the current
   movement got out of inventory between t=current and T=END. These items are not
   present in the final inventory and can be discarded.
   @unbalanced_inventory=@unbalanced_inventory - quantity

Parameter lowest_value_test compares latest price and FILO price and takes the
smallest one.

*/

SET @unbalanced_output=0.0, @total_asset_price=0.0, @running_total_asset_price=0.0, @latest_price=null, @running_quantity=0.0
<dtml-var sql_delimiter>
SELECT
  (IF(quantity <= 0, @latest_price, @latest_price:=IFNULL(@latest_price, total_price/quantity))) as dummy_latest_price,
  (@running_total_asset_price:=@running_total_asset_price +
    IF(quantity <= 0, 0,
    total_price/quantity * GREATEST(0, quantity-@unbalanced_output))) as running_total_asset_price,
  (@unbalanced_output:=GREATEST(0, @unbalanced_output-quantity)) as dummy,
  (@running_quantity:=@running_quantity + quantity) as running_quantity,
  <dtml-if "lowest_value_test">
   (@total_asset_price:=LEAST(@running_total_asset_price, @running_quantity*@latest_price)) as total_asset_price
  <dtml-else>
   (@total_asset_price:= @running_total_asset_price) as total_asset_price
  </dtml-if>
FROM
 stock, catalog
WHERE
  <dtml-var where_expression>
ORDER by date DESC


</dtml-if>