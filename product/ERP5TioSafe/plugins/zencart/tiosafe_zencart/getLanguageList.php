<?php
  include('tiosafe_config.php');

 
  $language_id = getDefaultLanguageID($db);
  
  $req_select  = "SELECT languages_id AS id, ";
  $req_select .= "name AS title ";
  $req_select .= "FROM ". TABLE_LANGUAGES ."  ";
   
  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);

  $db->close();

?>