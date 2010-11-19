<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql which render the language list
  $sql = "SELECT id_lang AS id, name AS title FROM ".constant('_DB_PREFIX_')."lang";

  echo executeSQL($sql);
?>
