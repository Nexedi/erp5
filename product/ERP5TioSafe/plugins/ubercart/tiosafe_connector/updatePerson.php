<?php
include('database.php');

if (isset($_POST['id'])) {
    $id = $_POST['id'];
    $person_sql = "UPDATE uc_orders SET ";
}
if (isset($_POST['firstname'])) {
    $firstname = $_POST['firstname'];
    $person_sql .= sprintf(" billing_first_name = %s, ", $firstname);
}
if (isset($_POST['lastname'])) {
    $lastname = $_POST['lastname'];
    $person_sql .= sprintf(" billing_last_name = %s, ", $lastname);
}
if (isset($_POST['email'])) {
    $email = $_POST['email'];
    $person_sql .= sprintf(" primary_email = %s, ", $email);
}
if (isset($id)){
  $person_sql .= " order_id = order_id WHERE order_id=$id";
  mysql_query($person_sql) or die(mysql_error());
}

?>
