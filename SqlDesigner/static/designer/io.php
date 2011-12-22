<?php
/*
	WWW SQL Designer, (C) 2005-2007 Ondra Zara, o.z.fw@seznam.cz

    This file is part of WWW SQL Designer.

    WWW SQL Designer is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    WWW SQL Designer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with WWW SQL Designer; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA	
*/

/* mysql: */
	define('SERVER','localhost');
	define('USER','');
	define('PASSWORD','');
	define('DB','');
	define('TABLE','wwwsqldesigner');
	$conn = mysql_connect(SERVER,USER,PASSWORD);
	mysql_select_db(DB);
/**/

	$action = 0; /* defaultni je export */
	if (isset($_GET['import'])) {
		$action = 1;
	}
	
	/**********  CODE BEGIN  **********/

	if (isset($_GET['show'])) {
		$action = 2;
	}

	/**********  CODE END  **********/

	switch ($action) {
		case 0:
			$key = (isset($_POST['key']) ? $_POST['key'] : '');
			$data = (isset($_POST['data']) ? $_POST['data'] : '');
			if (!$key) {
				die();
			} else {
				$key = mysql_real_escape_string($key);
				if (get_magic_quotes_gpc() || get_magic_quotes_runtime()) {
				   $data = stripslashes($data);
				}
				$data = mysql_real_escape_string($data);
				$r = mysql_query("SELECT * FROM ".TABLE." WHERE keyword = '".$key."'");
				if (mysql_num_rows($r) > 0) {
					mysql_query("UPDATE ".TABLE." SET data = '".$data."', dt=NOW() WHERE keyword = '".$key."'");
				} else {
					mysql_query("INSERT INTO ".TABLE." (keyword, data, dt) VALUES ('".$key."', '".$data."', NOW())");
				}
				mysql_free_result($r);
			}
		break;
		
		case 1:
			$key = (isset($_GET['key']) ? $_GET['key'] : '');
			$key = mysql_real_escape_string($key);
 			$r = mysql_query("SELECT * FROM ".TABLE." WHERE keyword = '".$key."'");
			if ($data = mysql_fetch_array($r)) {
				$d = str_replace(array("\n","\r"),'',$data['data']);
				echo $d;
			}
			mysql_free_result($r);
		break;

		/**********  CODE BEGIN  **********/

		case 2:
		 	$r = mysql_query("SELECT keyword, dt FROM ".TABLE." ORDER BY dt DESC");
			while ($row = mysql_fetch_array($r, MYSQL_BOTH)) {
  				printf ("%s:  %s\n", $row["dt"], $row["keyword"]);
			}
			mysql_free_result($r);
		break;

		/**********  CODE END  **********/
	}
	
?>
