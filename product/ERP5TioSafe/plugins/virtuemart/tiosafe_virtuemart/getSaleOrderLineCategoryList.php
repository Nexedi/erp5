<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query 1string and complete the SQL query
  $order_item_id = "";
  $order_id = "";
  if(isset($_POST['sale_order_id']))
    $order_id = $_POST['sale_order_id'];
  if(isset($_POST['sale_order_line_id']))
    $order_item_id = $_POST['sale_order_line_id'];
 //$order_id=;
 if($order_id !="") {
    // Generate the query
    $req_select  = "SELECT categ.category_id AS id, ";
    $req_select .= "category_name AS category  ";
    //$req_select .= "item.order_id AS order_id,  ";
    //$req_select .= "item.product_id AS product_id  ";
    $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_category categ  ";
    $req_select .= "RIGHT OUTER JOIN ".constant('_VM_TABLE_PREFIX_')."_product_category_xref prod_categ ";
    $req_select .= "ON categ.category_id=prod_categ.category_id ";
    $req_select .= "RIGHT OUTER JOIN ".constant('_VM_TABLE_PREFIX_')."_order_item item ON item.product_id=prod_categ.product_id ";
    $req_select .= "WHERE item.order_id='".$order_id."' ";
    if($order_item_id != "")
      $req_select .= "AND item.order_item_id='".$order_item_id."' ";
    $req_select .= "AND category_name != ''";
    //echo $req_select;
    $req = mysql_query($req_select) or die('\nInvalid query: '.$req_select.' '. mysql_error());

   
    if(mysql_num_rows($req) > 0) {
        $xml = '<xml>';
        while ($row = mysql_fetch_assoc($req)) {
          $xml .= '<object>';
          
          foreach ($row as $fieldname => $fieldvalue) {
            if ($fieldname == 'category') {
              $categ_id = $row['id'];
              $category_path = getCategoryPath($categ_id,$parent_id=0)."/".getCategoryName($categ_id);
              $category_path = constant('_COLLECTION_CIM_ID_')."".$category_path;
              $xml .= '<'.$fieldname.'>'.$category_path.'</'.$fieldname.'>';
            }
            else
              $xml .= '<'.$fieldname.'>'.$fieldvalue.'</'.$fieldname.'>';
          }
          
          $xml .= '</object>';
        }

        if($order_item_id != "") $xml .= getProductAttributeFormattedList($order_item_id);

        $xml .= '</xml>';

        header('Content-type: text/xml');
        echo $xml;
     }
     else
       $xml="<xml></xml>";    
  }
  else 
    echo '\nInvalid query: No parameter given!';

 

 mysql_close();
 ?>