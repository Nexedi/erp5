<?php
function executeSQL($sql)
{
    $path = explode('/modules',dirname(__FILE__));

    $db = mysql_connect(constant('_DB_SERVER_'), constant('_DB_USER_'), constant('_DB_PASSWD_'));
    mysql_query("SET NAMES UTF8");
    mysql_select_db(constant('_DB_NAME_'),$db);
    $req = mysql_query($sql);
    if (!$req) {
        die('\nInvalid query: ' . mysql_error());
    }

    if (empty($req)) {
        return mysql_error();
    }

    if (gettype($req) == 'boolean'){
        return;
    }

    $result = "<xml>";
    while($data = mysql_fetch_assoc($req))
        {
            $result .= "<object>";
            foreach(array_keys($data) as $key)
                {
                    $result .= "<$key>$data[$key]</$key>";
                }
            $result .= "</object>";
        }
    $result .= "</xml>";
    mysql_close();
    return $result;
}
?>
