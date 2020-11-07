<?php
	$servername = 'localhost,1433'; // 서버 ip port
	$dbName = ''; // DB 명
	$dbUser = ''; //DB 계정 명
	$dbPassword = ''; //DB 계정 패스워드

	$connectionInfo = array(
		"Database" => $dbName,
		"UID" => $dbUser,
		"PWD" => $dbPassword
	);

	$conn = sqlsrv_connect($dbServer, $connectionInfo);
	if( $conn ) {
		echo "connection true";
	}
	else{
		echo "connection failed";
		die( print_r( sqlsrv_errors(), true));
	}
	$query = "select * from Posts where id='".$_GET['id']."'";
	$stmt = sqlsrv_query($conn, $query);
	if ($stmt === false) {
		die( print_r (sqlsrv_errors(), true));
	}	
	else {
		while($row = sqlsrv_fetch_array($stmt)) {
			echo $row[0];
			echo $row[1];
		}
	}
    $query = "select * from hpcnt_prob where id='admin' and pw='{$_GET[pw]}'";
?>
