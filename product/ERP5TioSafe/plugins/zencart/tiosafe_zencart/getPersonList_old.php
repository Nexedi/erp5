
<?php
  include('tiosafe_config.php');

  $customer_id = "";
  if(postNotEmpty ('person_id'))
    $customer_id = $_POST['person_id'];
  
  $req_select  = "SELECT customers_id AS id, ";
  $req_select .= "CONCAT(customers_firstname, ' ', customers_lastname) AS title,   ";
  $req_select .= "customers_firstname AS firstname, ";
  $req_select .= "customers_lastname AS lastname, ";
  $req_select .= "customers_email_address AS email, ";
  $req_select .= "customers_dob AS birthday ";
  $req_select .= "FROM ". TABLE_CUSTOMERS;
  $req_select .= " WHERE customers_firstname != '' AND customers_lastname != '' AND customers_email_address != ''";
  if($customers_id != "" )
    $req_select .= "AND customers_id='".$customers_id."' ";
  $req_select .= "ORDER BY firstname ASC, lastname ASC, email ASC";


  //$person_list = $db->Execute($req_select);
  //print_r($person_list);
  
  echo executeSQL($req_select, $db);
  /*
  $xml = '<xml>';

  while (!$person_list->EOF) {
    $xml .= '<object>';
    $xml .= '<id>' . $person_list->fields['customers_id'] . '</id>';
    $xml .= '<title>' . $person_list->fields['customers_gender'] . '</title>';
    $xml .= '<firstname>' . $person_list->fields['customers_firstname'] . '</firstname>';
    $xml .= '<lastname>' . $person_list->fields['customers_lastname'] . '</lastname>';
    $xml .= '<email>' . $person_list->fields['customers_email_address'] . '</email>';
    $xml .= '<birthday>' . $person_list->fields['customers_dob'] . '</birthday>';
    $xml .= '</object>';
    $person_list->MoveNext();
  }

  $xml .= '</xml>';  */

  header('Content-type: text/xml');
  echo $xml;
?> 
