<?php

/* 
	import schema from existing database
*/


/* CHANGE THIS TO REFLECT YOUR ODBC SETTINGS: */
  $drivername = 'SQL Server';
  $servername = 'COMPUTER\SQLEXPRESS';
  $dbname = 'database';
  
  $dnsstring = "DRIVER={".$drivername."};SERVER=$servername;DATABASE=$dbname";
	$conn = odbc_connect($dnsstring,'','');
  
/**/


/* CONVERSION ARRAYS */
$tmp_conv['Integer'] = array('NUMBER','NUMBERIC','DECIMAL','INTEGER','INT','INT4');
$tmp_conv['Small Integer'] = array('SMALLINT','BOOLEAN','INT2','BOOL');
$tmp_conv['Single precision'] = array('FLOAT','REAL','FLOAT4');
$tmp_conv['Double precision'] = array('DOUBLE','DOUBLE PRECISION');
$tmp_conv['String'] = array('CHARACTER','VARCHAR','CHAR','NCHAR','NVARCHAR');
$tmp_conv['Text'] = array('TEXT','LONG VARCHAR','CLOB');
$tmp_conv['Binary'] = array('VARBINARY','BINARY');
$tmp_conv['Large binary'] = array('LONG VARBINARY','BLOB');
$tmp_conv['Date'] = array('DATE');
$tmp_conv['Time'] = array('TIME');
$tmp_conv['Datetime'] = array('DATETIME');
$tmp_conv['Timestamp'] = array('TIMESTAMP');
$tmp_conv['XML'] = array('LONG XML');
$tmp_conv['? UNKNOWN ?'] = array('','INTERVAL');
$conv = array();

	function convert($type) {
		global $conv;
		$type = strtolower($type);
		if (isset($conv[$type])) {
			return $conv[$type];
		} else {
			echo $type;
			return $conv[''];
		}
	}

	function prepare_conversion() {
		global $tmp_conv;
		foreach ($tmp_conv as $value=>$arr) {
			for	($i=0;$i<count($arr);$i++) {
				$GLOBALS['conv'][strtolower($arr[$i])] = $value;
			}
		} /* foreach type */
	}

	function generate_xml($tables) {
		$out = 	'<?xml version="1.0" ?>'."\n";
		$out .= '<!-- PHP/ODBC XML export -->'."\n";
		$out .= '<sql>'."\n";
		
		foreach ($tables as $tmp) {
			$name = $tmp[2];
			$cols = $tmp[0];
			$out .= "\t".'<table title="'.$name.'" >'."\n";
				for ($i=0;$i<count($cols);$i++) {
					$col = $cols[$i];
					$str = '';
					if ($col['nn']) {
						$str .= ' nn="nn"';
					}
					if ($col['pk']) {
						$str .= ' pk="pk"';
					}
					if ($col['special']) { /* spec */
						$str .= ' special="'.$col['special'].'"';
					}
					$out .= "\t\t".'<row'.$str.'>'."\n";
					$out .= "\t\t\t".'<title>'.$col['name'].'</title>'."\n";
					$out .= "\t\t\t".'<default>'.$col['default'].'</default>'."\n";
					$out .= "\t\t\t".'<type>'.convert($col['type']).'</type>'."\n";
					$out .= "\t\t".'</row>'."\n";
				}
			$out .= "\t".'</table>'."\n";
		} /* pokud tabulka existuje */
		$out .= '</sql>'."\n";
		echo $out;
	}

	function get_cols(&$conn,$table) {  
    global $dbname;
  
		$cols = array();
		$keys = array();
    
//    $table = 'dbo.'.$table;
    
		$r = odbc_primarykeys($conn,$dnname,'%',$table);
		while ($row = odbc_fetch_array($r)) {
			$keys[] = $row['COLUMN_NAME'];
		}
		$r = odbc_columns($conn,$dbname,'%',$table,'%');
		while ($row = odbc_fetch_array($r)) {
    
//      print_r($row);
    
			$c = array();
			$c['name'] = htmlentities($row['COLUMN_NAME']);
			$c['type'] = $row['TYPE_NAME'];
			$c['special'] = '';
			if (isset($row['COLUMN_SIZE'])) $c['special'] = $row['COLUMN_SIZE'];
			if (isset($row['LENGTH'])) $c['special'] = $row['LENGTH'];
			$c['nn'] = ($row['NULLABLE']==0);
			$c['default'] = str_replace("'",'',$row['COLUMN_DEF']);
			$c['pk'] = in_array($row['COLUMN_NAME'],$keys);
			$cols[] = $c;
		}
		return $cols;
	}
	
	function cmp($arr1,$arr2) {
		$a = $arr1[1]; /* count of cols in 1st array */
		$b = $arr2[1]; /* count of cols in 2nd array */
		if ($a == $b) {
			return 0;
		}
		return ($a < $b) ? -1 : 1;
	}

	prepare_conversion();
	$table_names = array();
	$tables = array();
	$r = odbc_tables($conn);
  
	while ($t = odbc_fetch_array($r)) {
  
//    print_r($t);
  
		$type = ($t['TABLE_TYPE'] == 'TABLE');
		$owner = true;
		if (isset($t['TABLE_OWNER'])) $owner = (strtolower($t['TABLE_OWNER']) != 'information_schema');
		if ($type && $owner) {
			$table_names[] = $t['TABLE_NAME'];
		}
	}
	for ($i=0;$i<count($table_names);$i++) {
		$cols = get_cols($conn,$table_names[$i]);
    
		$cnt = count($cols);
		$tables[] = array($cols,$cnt,$table_names[$i]);
	}
	usort($tables,"cmp");
	
	generate_xml($tables);
?>
