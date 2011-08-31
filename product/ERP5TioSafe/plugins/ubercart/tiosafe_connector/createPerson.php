<?php
include('database.php');
$firstname = ""; 
$lastname = "";
$email = "";

if (isset($_POST['firstname'])) {
    $firstname = $_POST['firstname'];
}
if (isset($_POST['lastname'])) {
    $lastname = $_POST['lastname'];
}
if (isset($_POST['email'])) {
    $email = $_POST['email'];
}

if ($firstname!="" and $lastname!="" and $email!=""){
  $req_exist_user = mysql_query("SELECT * from users where mail=$email") or die(mysql_error());
  $user_rows = mysql_num_rows($req_exist_user);
  if ($user_rows == 0){
      $user_insert_sql = sprintf("INSERT INTO users (mail, created, status, init) VALUES (%s,%d, %d, %s)", 
	      GetSQLValueString($email,"text"), 
	      GetSQLValueString(time(),"int"), 
	      GetSQLValueString(1,"int"), 
	      GetSQLValueString($email,"text"));     
      mysql_query($user_insert_sql) or die(mysql_error());
      $uid = mysql_insert_id();
  }else{
      $result = mysql_fetch_array($req_exist_user);
      $uid = $result["uid"];  
  }

  $req_exist_customer = mysql_query("SELECT * from uc_orders where primary_email=$email and  billing_first_name=$firstname and billing_last_name=$lastname") or die(mysql_error());
  $customer_rows = mysql_num_rows($req_exist_customer);
  if ($customer_rows == 0){
    $customer_sql = sprintf("INSERT INTO uc_orders (uid, primary_email, billing_first_name, billing_last_name, created, modified, order_status) VALUES (%d, %s, %s, %s, %d, %d, '%s')", 
	    GetSQLValueString($uid,"int"), 
	    GetSQLValueString($email,"text"), 
	    GetSQLValueString($firstname,"text"), 
	    GetSQLValueString($lastname,"text"),
	    GetSQLValueString(time(),"int"),
	    GetSQLValueString(time(),"int"),
	    GetSQLValueString('pending',"text")); 
    mysql_query($customer_sql) or die(mysql_error());
  }
}  


?>