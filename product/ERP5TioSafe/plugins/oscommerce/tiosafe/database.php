<?php
/**
 * Executes SELECT sql query and returns result as XML
 */
function executeSQL($sql)
{
		include_once('../includes/functions/database.php');

    $req = tep_db_query($sql);

    $result = "<xml>";

    while($data = tep_db_fetch_array($req))
        {
            $result .= "<object>";
            
            foreach($data as $key => $value)
                {
                    $result .= "<$key>$value</$key>";
                }
            $result .= "</object>";
        }
    $result .= "</xml>";

    return $result;
}

/**
 * Executes SELECT sql query and returns result as array
 */
function executeSQLtoArray($sql)
{
  $req = tep_db_query($sql);

  $result = array();

  while($data = tep_db_fetch_array($req))
  {
    $properties = array();

    foreach($data as $key => $value)
    {
      $properties[$key] = $value;
    }

    if (count($properties)) {
      $result[] = $properties;
  }
}

  return $result;
}
?>
