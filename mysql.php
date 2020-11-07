<?php

    $servername = getenv('MYSQL_IP');
    $username = getenv('MYSQL_ROOT_USER');
    $password = getenv('MYSQL_ROOT_PASSWORD');

    $connect = mysql_connect($servername,$username,$password) or die("db error");
    mysql_select_db("hpcnt",$connect);
    $query = "select * from hpcnt_prob where id='admin' and pw='{$_GET[pw]}'";
    $result = mysql_query($query);
    if(!$result) {
	    echo 'error :'.mysql_error();
    }
    while( $row = mysql_fetch_array($result)) {
	    echo 'id : '.$row[0];
	    echo '<br>';
	    echo 'pw :'.$row[1];
    } 
?>
