<?php
//use the active database of drupal
include_once('../../sites/default/settings.php');
include_once('../../includes/bootstrap.inc');
include_once('../../includes/database.inc');
include_once('../../includes/database.mysql.inc');
include_once('../../includes/common.inc');
db_connect($db_url);

function executeSQL($sql)
{
    $req = mysql_query($sql);
    if (!$req) {
        die('\nInvalid query: ' .$sql.'\n'. mysql_error());
    }
    $result = "<xml>";
    while($data = mysql_fetch_assoc($req))
        {
            $result .= "<object>";
            foreach(array_keys($data) as $key)
                {
                    if ($key == 'start_date' or $key == 'stop_date'){
                      $result .= "<$key>".format_date($data[$key],'custom', 'Y/m/d')."</$key>";
                    }else{
                      $result .= "<$key>$data[$key]</$key>";
                    }
                }
            $result .= "</object>";
        }
    $result .= "</xml>";
    mysql_close();    
    return $result;
}

function GetSQLValueString($theValue, $theType, $theDefinedValue = "",
$theNotDefinedValue = "")
{
 //$theValue = (!get_magic_quotes_gpc()) ? addslashes($theValue) : $theValue;
 switch ($theType) {
   case "text":
     $theValue = ($theValue != "") ?  $theValue  : "NULL";
     break;
   case "long":
   case "int":
     $theValue = ($theValue != "") ? intval($theValue) : "NULL";
     break;
   case "double":
     $theValue = ($theValue != "") ? "'" . doubleval($theValue) . "'" : "NULL";
     break;
   case "date":
     $theValue = ($theValue != "") ? "'" . $theValue . "'" : "NULL";
     break;
   case "defined":
     $theValue = ($theValue != "") ? $theDefinedValue : $theNotDefinedValue;
     break;
 }
 return $theValue;
}

function getDefaultSiteCurency(){
  $query = mysql_query("SELECT * FROM variable WHERE name='uc_currency_code'") or die(mysql_error());
  $result = mysql_fetch_array($query);
  $currency_code = "";
  if (mysql_num_rows($query)!=0){
    $value = $result["value"]; // stored like this: s:3:"USD";
    $value_list = split(";", $value);
    $currency_code_list = split(":", $value_list[0]);
    $currency_code = $currency_code_list[2];
  }
  return $currency_code;
}
function getVatTaxRate($order_id){
  $query = mysql_query("SELECT title, rate FROM uc_order_line_items oli left outer join uc_taxes tx on oli.title = tx.name WHERE order_id='$order_id' and type='tax'") or die(mysql_error());
  $result = mysql_fetch_array($query);
  $rate = 0;
  if (mysql_num_rows($query)!=0){
    $rate = $result["rate"]; 
  }
  return $rate;
}


function getLangageFor($code){
  $query = mysql_query("SELECT * FROM langages WHERE langage='$code'") or die(mysql_error());
  $result = mysql_fetch_array($query);
  if (mysql_num_rows($query)!=0){
    return $result["name"];
  }
  return $code;
}


function getCountriesInfo($name) {  
  $query = mysql_query("SELECT iso2, iso3, name, printable_name, numcode FROM countries_api_countries WHERE printable_name='$name'") or die(mysql_error());
  $result = array();
  if (mysql_num_rows($query)!=0){
    $result = mysql_fetch_array($query);
  }
  return $result;
}

function getParentCategory($cat_id){
  $sql = "SELECT th.parent as id_category, td.name as title ";
  $sql .= "FROM term_hierarchy th " ;
  $sql .= "LEFT OUTER JOIN term_data td ON th.parent = td.tid ";
  $sql.= "WHERE th.tid=$cat_id ";
  $req = mysql_query($sql);
  $result = mysql_fetch_array($req);
  return $result;
}

function getProductCategory($product_id){
  if ((empty($product_id)) or ($product_id==0) or ($product_id=="")){
    return "";
  }
  $sql = "SELECT tn.tid as id_category, v.name as base_category, td.name as category ";
  $sql .= "FROM term_node tn " ;
  $sql .= "LEFT OUTER JOIN term_data td ON tn.tid = td.tid ";
  $sql .= "LEFT OUTER JOIN vocabulary v ON v.vid = td.vid ";
  $sql.= "WHERE nid=$product_id ";
  $req = mysql_query($sql);
  $count = mysql_num_rows($req);
  $result = array();
  if ($count>0){
    while($res = mysql_fetch_array($req)){
      $category_list = array();    
      $id_category =  $res["id_category"];
      $base_category =  $res["base_category"];
      $category =  $res["category"];  
      $category_list[] = $category;
      while($id_category!=0){
	$parent_info = getParentCategory($id_category);
	$id_category = $parent_info["id_category"];
	$category = $parent_info["title"]; 
	if ($id_category!=0){
	  $category_list[] = $category;
	}
      }
      if (isset($base_category)){
	$category_list[] = $base_category;
	$full_category = implode("/", array_reverse($category_list));
	$result[] = $full_category;
      }  
    }
  }
  return $result;
}

function python_utf8_decode($text) {
 $text = str_replace("\xc3\xa9", 'é', $text);
 $text = str_replace("\xc3\xa8", 'è', $text);
 $text = str_replace("\xc3\xaa", 'ê', $text);
 $text = str_replace("\xc3\xa7", 'ç', $text);
 $text = str_replace("\xc3\xb9", 'ù', $text);
 $text = str_replace("\xc3\xa0", 'à', $text);
 $text = str_replace("\xc3\x89", 'É', $text);
 $text = str_replace("\xc3\x8a", 'Ê', $text);
 $text = str_replace("\xc3\x8b", 'Ë', $text);
 $text = str_replace("\xc3\x8e", 'Î', $text);
 $text = str_replace("\xc3\x8f", 'Ï', $text);
 $text = str_replace("\xc3\xab", 'ë', $text);
 $text = str_replace("\xc3\xb4", 'ô', $text);
 $text = str_replace("\xc3\xb6", 'ö', $text);
 $text = str_replace("\xc3\xa2", 'â', $text);
 $text = str_replace("\xc3\xbb", 'û', $text);
 $text = str_replace("\xc3\x87", 'Ç', $text);
 $text = str_replace("\xc3\x9b", 'Û', $text);
 $text = str_replace("\xc3\x94", 'Ô', $text);
 $text = str_replace("\xc3\x96", 'Ö', $text);
 $text = str_replace("\xc3\x9c", 'Ü', $text);
 $text = str_replace("\xc3\xa1", 'á', $text);
 $text = str_replace("\xc3\xa4", 'ä', $text);
 $text = str_replace("\xc3\x82", 'Â', $text);
 $text = str_replace("\xc3\x84", 'Ä', $text);
 $text = str_replace("\xc3\x81", 'Á', $text);
 $text = str_replace("\xc3\x83", 'Ã', $text);
 $text = str_replace("\xc3\x84", 'Ä', $text);
 $text = str_replace("\xc3\x85", 'Å', $text);
 $text = str_replace("\xc3\xb1", 'ñ', $text);
 $text = str_replace("\xc2\xa9", '©', $text);
 $text = str_replace("\xc2\xbb", '»', $text);
 $text = str_replace("\xc2\xab", '«', $text);
 $text = str_replace("\xc3\x89", 'É', $text);
 $text = str_replace("\xc3\xbc", 'ü', $text);
 $text = str_replace("\xc3\xbf", 'ÿ', $text);
return $text;
}

?>
