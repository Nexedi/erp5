<?php exit();
  include("includes/config.inc.php");
  include("includes/function.php");

  
  //Get the query string and complete the SQL query
  $user_id = "";
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
 
  
  // Generate the query
  if ($user_id != "") {
    //XXX Delete the customer informations
    $req_delete  = "DELETE FROM ".constant('_VM_TABLE_PREFIX_')."_user_info WHERE user_id=".$user_id."";
    executeSQL($req_delete);
    // Delete the user's informations
    $req_delete1 = "DELETE FROM ".constant('_JOOMLA_TABLE_PREFIX_')."users WHERE id=".$user_id."";
    executeSQL($req_delete1);
    $req_delete1 = "DELETE FROM ".constant('_JOOMLA_TABLE_PREFIX_')."core_acl_aro WHERE value=".$user_id."";
    echo executeSQL($req_delete1);
  }
  else 
    echo '\nInvalid query: No parameter given!';
  mysql_close();

 ?>