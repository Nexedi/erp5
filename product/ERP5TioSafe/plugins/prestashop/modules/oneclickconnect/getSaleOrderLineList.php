<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql query which allows to render the sale order line
  $sql = "SELECT ";
  $sql .= "DISTINCT(".constant('_DB_PREFIX_')."order_detail.product_id) AS id_product, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.id_order_detail AS id, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.product_name AS title, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.product_reference AS reference, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.product_id AS resource, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.product_attribute_id AS id_group, ";
  $sql .= "FORMAT(".constant('_DB_PREFIX_')."order_detail.product_quantity, 2) AS quantity, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.product_price AS price, ";
  $sql .= constant('_DB_PREFIX_')."order_detail.tax_rate AS VAT ";

  # from which tables data come
  $sql .= "FROM ".constant('_DB_PREFIX_')."orders ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."order_detail ";
  $sql .= "ON ".constant('_DB_PREFIX_')."order_detail.id_order=".constant('_DB_PREFIX_')."orders.id_order ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."currency ";
  $sql .= "ON ".constant('_DB_PREFIX_')."currency.id_currency=".constant('_DB_PREFIX_')."orders.id_currency ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product_lang ";
  $sql .= "ON ".constant('_DB_PREFIX_')."product_lang.id_product=".constant('_DB_PREFIX_')."order_detail.product_id ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product ";
  $sql .= "ON ".constant('_DB_PREFIX_')."product.id_product=".constant('_DB_PREFIX_')."order_detail.product_id ";

  # restrict the render
  if (isset($_POST['sale_order_id'])){
      $sql .= "WHERE ";
      $sql .= constant('_DB_PREFIX_')."orders.id_order=".$_POST['sale_order_id'];
      if (isset($_POST['product_id'])){
          $sql .= " AND ".constant('_DB_PREFIX_')."order_detail.product_id=".$_POST['product_id'];
      }
  }

#  # CHECK: is it usefull to provie an order ?
#  $sql .= " ORDER BY ";
#  $sql .= constant('_DB_PREFIX_')."order_detail.product_name ASC, ";
#  $sql .= constant('_DB_PREFIX_')."order_detail.product_reference ASC ";

  echo executeSQL($sql);
?>
