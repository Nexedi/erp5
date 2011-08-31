<?php
  /**
   * Sometimes it's not easy to do everything with a query.
   * So we get what we want from the database as objects and then manipulate them.
   * Every result of a the query is put in an object with puts info in array.
   */
  class Object_query {
    private $object_list;
    private $query;

    public function __construct($query) {
      include_once('database.php');
      include_once('functions.php');
      include_once('../includes/configure.php');
      include_once('../includes/database_tables.php');
      include_once('../includes/functions/database.php');
      
      tep_db_connect() or die('Unable to connect to database');

      $this->query = $query;
      $this->object_list = executeSQLtoArray($this->query);

      tep_db_close();
    }

    public function isRequestOk() {
      if (count($this->object_list)) return true;
      return false;
    }

    public function getCollection() {
      return $this->object_list;
    }

  }
?>
