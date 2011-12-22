<?php
	$keyword="";
	if (isset($_GET["keyword"])) {
		$keyword = $_GET["keyword"];
	}
	require_once('./config.php');
	if(file_exists("./lang/$fileLang")){
		require_once("./lang/$fileLang");
	}else {
		require_once("./lang/default.php");
	}
?>
<html>
<head>
<!--
	WWW SQL Designer, (C) 2005-2007 Ondra Zara, o.z.fw@seznam.cz
	Version: 1.4

    This file is a main part of WWW SQL Designer.

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
-->

	<title>SQL Designer</title>
	<link rel="stylesheet" type="text/css" href="styles/style.css" />     
	<script type="text/javascript" src="js/settings.js"></script>  <!-- globalni nastaveni -->
	<script type="text/javascript" src="styles/style.js"></script> <!-- globalni nastaveni -->
	<script type="text/javascript" src="js/generic.js"></script>   <!-- funkce nezavisle na projektu -->
	<script type="text/javascript" src="js/ajax.js"></script>      <!-- ajax -->
	<script type="text/javascript" src="js/sql_types.js"></script> <!-- sql datove typy -->
	<script type="text/javascript" src="js/main.js"></script>      <!-- hlavni skript -->
	<script type="text/javascript" src="js/objects.js"></script>   <!-- deklarace objektu -->
	<script type="text/javascript" src="js/animator.js"></script>  <!-- animovane pridani/ubrani radku -->
	<script type="text/javascript" src="js/io.js"></script>  	   <!-- import/export -->
	
</head>

<body onload="load('<?php echo $keyword; ?>')">
	<div id="root">
		<div id="bar"> <!-- navigacni lista nahore -->
			<div id="shadow"> <!-- stin listy na jejim spodku -->
			</div>
			<div id="table_admin">
				<div id="table_admin_label"><?php echo $lang['table']['title']; ?></div>
				<label for="table_name" id="table_name_label"><?php echo $lang['table']['name']; ?></label>
				<div id="table_add_button" class="button"><?php echo $lang['table']['add']; ?></div>
				<div id="table_del_button" class="button"><?php echo $lang['table']['delete']; ?></div>
				<div id="table_move_button" class="button"><?php echo $lang['table']['align']; ?></div>
				<div id="table_clear_button" class="button"><?php echo $lang['table']['clear']; ?></div>
				<input type="text" id="table_name" />
			</div>
			<div id="row_admin">
				<div id="row_admin_label"><?php echo $lang['row']['title']; ?></div>
				<label for="row_name" id="row_name_label"><?php echo $lang['row']['name']; ?></label>
				<div id="row_add_button" class="button"><?php echo $lang['row']['add']; ?></div>
				<div id="row_del_button" class="button"><?php echo $lang['row']['delete']; ?></div>
				<div id="row_up_button" class="button"><?php echo $lang['row']['up']; ?></div>
				<div id="row_down_button" class="button"><?php echo $lang['row']['down']; ?></div>
				<input type="text" id="row_name" />
				
				<input type="radio" id="row_primary" title="Primary Key" />
				<label for="row_primary" id="row_primary_label" title="Primary Key">PK</label>

				<label for="row_index" id="row_index_label" title="Index" >IDX</label>
				<input type="checkbox" id="row_index" title="Index" />

				<label for="row_notnull" id="row_notnull_label" title="Not NULL" >NN</label>
				<input type="checkbox" id="row_notnull" title="Not NULL" />

				<label for="row_default" id="row_default_label"><?php echo $lang['row']['default']; ?></label>
				<input type="text" id="row_default" />

				<label for="row_type" id="row_type_label"><?php echo $lang['row']['type']; ?></label>
				<select id="row_type" /></select>

				<div id="row_spec_1">(</div>
				<input type="text" id="row_spec" /></select>
				<div id="row_spec_2">)</div>
			</div>

			<div id="io_admin">
				<div id="io_admin_label"><?php echo $lang['io']['title']; ?></div>
				<label for="io_select" id="io_select_label"><?php echo $lang['io']['method']; ?></label>
				<div id="io_button" class="button"><?php echo $lang['io']['go']; ?></div>
				<div id="io_settings_button" class="button"><?php echo $lang['io']['settings']['title']; ?></div>
				<select id="io_select">
					<option selected="selected" value="db_import"><?php echo $lang['io']['settings']['db_import']; ?></option>
					<option value="xml_out"><?php echo $lang['io']['settings']['xml_out']; ?></option>
					<option value="xml_in"><?php echo $lang['io']['settings']['xml_in']; ?></option>
					<option value="db_out"><?php echo $lang['io']['settings']['db_out']; ?></option>
					<option value="db_out_as"><?php echo $lang['io']['settings']['db_out_as']; ?></option>
					<option value="db_in"><?php echo $lang['io']['settings']['db_in']; ?></option>
					
					<!----------  CODE BEGIN  ---------->

					<option value="show_keywords"><?php echo $lang['io']['settings']['show_keywords']; ?></option>
					<option value="print_view"><?php echo $lang['io']['settings']['print_view']; ?></option>
					
					<!----------  CODE END  ---------->

					<option value="mssql"><?php echo $lang['io']['settings']['mssql']; ?></option>
					<option value="mysql"><?php echo $lang['io']['settings']['mysql']; ?></option>
					<option value="propel"><?php echo $lang['io']['settings']['propel']; ?>	</option>
					<option value="symfony"><?php echo $lang['io']['settings']['symfony']; ?>	</option>
					<option value="oci"><?php echo $lang['io']['settings']['oci']; ?></option>
					<option value="postgresql"><?php echo $lang['io']['settings']['postgresql']; ?></option>
					<option selected="selected" value="sqlite"><?php echo $lang['io']['settings']['sqlite']; ?></option>
				</select>
			</div>
			<div id="position" style="padding-left:580px;"></div>
		</div>
		<div id="map"> <!-- experimentalni mapa -->
			<div id="map_"> <!-- cervene okenko v experimentalni mape -->
			</div>
		</div>
		<div id="io">
			<textarea id="area"></textarea>
			<input id="import" value="<?php echo $lang['io']['load']; ?>" type="button" />
			<input id="close" value="<?php echo $lang['io']['close']; ?>" type="button" onclick="javascript:document.getElementById('io').style.display='none'" />
		</div>
	</div>
	
</body>
</html>
