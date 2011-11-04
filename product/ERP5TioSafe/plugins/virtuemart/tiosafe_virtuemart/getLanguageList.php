<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  
 
   $req_select  = "SELECT params FROM gvi_components";
   //echo $req_select;

   header('Content-type: text/xml');
   echo executeSQL($req_select);


 mysql_close();
 ?>