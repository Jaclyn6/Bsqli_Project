<?php

    $servername = getenv('MYSQL_IP');
    $username = getenv('MYSQL_ROOT_USER');
    $password = getenv('MYSQL_ROOT_PASSWORD');


    echo "hi";
    $connect = mysql_connect($servername,$username,$password) or die("db error");
    mysql_select_db("hpcnt",$connect);
    $query = "select id from hpcnt_prob where id='admin' and pw='{$_GET[pw]}'";
    echo $query;
    $result = mysql_fetch_array(mysql_query($query)); 
    echo $result;
    if($result['id']) echo "<h2>Hello admin</h2>"; 
  
    $_GET[pw] = addslashes($_GET[pw]); 
    $query = "select pw from hpcnt_prob where id='admin' and pw='{$_GET[pw]}'"; 
    $result = mysql_fetch_array(mysql_query($query)); 
?>