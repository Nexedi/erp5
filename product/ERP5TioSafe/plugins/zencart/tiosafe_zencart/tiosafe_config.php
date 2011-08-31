<?php
  /**
  * boolean if true the autoloader scripts will be parsed and their output shown. For debugging purposes only.
  */
  define('DEBUG_AUTOLOAD', false);
  /**
  * boolean used to see if we are in the admin script, obviously set to false here.
  * DO NOT REMOVE THE define BELOW. WILL BREAK ADMIN
  */
  define('IS_ADMIN_FLAG', true);

  // Id of the CategoryIntegration Mapping of Collection
  define ("COLLECTION_CIM_ID", "Collection"); 
  
include('../includes/configure.php');
  include('../../includes/database_tables.php');
  include('../includes/functions/database.php');
  include('../includes/functions/general.php');
  include('function.php');

  // Load queryFactory db classes
  //echo DIR_FS_CATALOG . DIR_WS_CLASSES . 'db/' .DB_TYPE . '/query_factory.php'; 
  require(DIR_FS_CATALOG . DIR_WS_CLASSES . 'class.base.php');
  require(DIR_FS_CATALOG . DIR_WS_CLASSES . 'db/' .DB_TYPE . '/query_factory.php');
  $db = new queryFactory();
  $db->connect(DB_SERVER, DB_SERVER_USERNAME, DB_SERVER_PASSWORD, DB_DATABASE);
 
?>

