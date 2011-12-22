/*
	WWW SQL Designer, (C) 2005 Ondra Zara, o.z.fw@seznam.cz

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

var drag_lock = 0; /* hybeme-li tabulkou */
var new_table_flag = 0; /* cekame-li na click pro vytvoreni nove tabulky */
var new_table_name = ""; /* jak se bude nova jmenovat */
var table_array = Array(); /* ukazatele na tabulky */
var relation_array = Array(); /* ukazatele na relace */
var drag_start; /* prvni element dragu */
var rel_hover_lock = -1; /* mame zvyraznenou relaci */
var mouse_x,mouse_y; /* souradnice */
var table_admin, row_admin, io_admin; /* tooly na baru */

/* --------------------------------------------------------------------------- */

function renumber_indexes(limit) {
	var zIndex;
	for (var i=0;i<table_array.length;i++) 
		if (table_array[i]) {
			zIndex = parseInt(table_array[i]._div.style.zIndex);
			if (zIndex > limit) table_array[i]._div.style.zIndex = zIndex-1;
		}
}
 
function get_max_zIndex() {
	var max_zIndex = 0;
	var zIndex;
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i]) {
			zIndex = parseInt(table_array[i]._div.style.zIndex);
			if (zIndex > max_zIndex) max_zIndex = zIndex;
		}
	}
	return max_zIndex;
}

function raise_table(number) {
	row_admin.manageTable(table_array[number]);
	table_admin.manageTable(table_array[number]);
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i] && i != number) {
			/* deselectujeme ostatni tabulky a popripade jejich selectnuty radek */
			table_array[i].deselect();
			if (table_array[i].selectedRow) {
				table_array[i].selectedRow.deselect();
				table_array[i].selectedRow = null;
			}
		}
	}
	table_array[number].select();
	var old_zIndex = table_array[number]._div.style.zIndex;
	var max_zIndex = get_max_zIndex();
	renumber_indexes(old_zIndex);
	table_array[number]._div.style.zIndex = max_zIndex;
}

function update_map_() {
	var map_ = document.getElementById("map_");
	var win_x = parseInt(document.body.clientWidth);
	var win_y = parseInt(document.body.clientHeight);
	var scroll_x = parseInt(document.body.scrollLeft);
	var scroll_y = parseInt(document.body.scrollTop);
	map_.style.width = Math.round(win_x * MAP_SIZE / DESK_SIZE) - 2 + "px"; 
	map_.style.height = Math.round(win_y * MAP_SIZE / DESK_SIZE) - 2 + "px"; 
	map_.style.left = Math.round(scroll_x * MAP_SIZE / DESK_SIZE) + "px";
	map_.style.top = Math.round(scroll_y * MAP_SIZE / DESK_SIZE) + "px";
}

function update_bar() {
	var bar = document.getElementById("bar");
	bar.style.width = parseInt(document.body.clientWidth) + "px";
}

/* --------------------------------------- udalosti --------------------------------------- */


function global_event_mousedown(co) {
	/* 
		nekdo stiskl mysitko, co udelame?
		a) bylo to na necem, co zname
			aa) bylo to na tabulce, titlu nebo radku - zvedneme tabulku
			ab) bylo to na moveru - zahajime dragging
		b) bylo to nekde jinde - serem na to.
	*/
	var src = universalSource(co); 
	var number = src.getAttribute("parent_number");
	var type = src.getAttribute("element_type");
	if (new_table_flag) {
		/* umisteni nove tabulky */
		document.body.style.cursor = "default";
		var tmp = get_exact_coords(co);
		var table = add_table(tmp[0],tmp[1],new_table_name);
		var row = table.addRow("id",6);
		table.selectedRow = row;
		row.select();
		row_admin.manageTable(table);
		row_admin.manageRow(row);
		row.setPK();
		new_table_flag = 0;
		return;
	}
	if (type == TYPE_BAR) { return; } /* lista si to sefuje sama */
	
	if (type != null) {
		/* tedy to bylo na elementu, ktery reaguje */
		
		/* prve zvysime tabulku */
		if ((type == TYPE_TABLE) || (type == TYPE_TITLE) || (type == TYPE_ROW) || (type == TYPE_ROWTITLE)) {
			raise_table(number); 
		}
		
		/* a ted jeste, nemame-li zacit nejaky dragging... */
		if ((type == TYPE_TABLE) || (type == TYPE_MAP) || (type == TYPE_TITLE)) {
			mouse_x=co.clientX;
			mouse_y=co.clientY;
			drag_start = src;
			drag_lock = 1;
			src.style.cursor = "move"; 
		}
		
		/* pokud se hybe tabulkou, schovame relace */
		if ((type == TYPE_TABLE) || (type == TYPE_TITLE)) {
			for (var i=0;i<table_array[number].rows.length;i++) {
				if (table_array[number].rows[i]) {
					table_array[number].rows[i].hideRelations();
				}
			}
		}
		
		/* klik na radku - management, mozna zacatek tazeni relace */
		if ((type == TYPE_ROW) || (type == TYPE_ROWTITLE)) {
			var rownumber = parseInt(src.getAttribute("row_number"));
			table_array[number].selectRow(rownumber);
			row_admin.manageRow(table_array[number].rows[rownumber]);
			/* relaci zacneme tahnout jen pokud je to pk */
			if (table_array[number].rows[rownumber].pk) {
				drag_start = src;
			}
		} /* klik na radku */
		
	} else {
		/* 
			bylo to nekde v riti, coz patrne znaci ze na betonu
			v takovou chvili deselectneme tabulky
		*/
		table_admin.loseTable();
		row_admin.loseTable();
		for (var i=0;i<table_array.length;i++) {
			if (table_array[i]) {
				table_array[i].deselect();
				if (table_array[i].selectedRow) {
					table_array[i].selectedRow.deselect();
					table_array[i].selectedRow = null;
				}
			}
		} /* deselect vsech tabulek */
	} /* na betonu */
} /* click */


function global_event_mouseup(co) {
	var x,y;
	if (drag_start) {
		drag_start.style.cursor = "default";
	} else {
		return;
		/* koncime, neb to nebyl drag ale jen click */
	}
	
	/* ted uz vime, ze to byl konec dragu. ale je vic moznosti - posun tabulky, minimapa, relace, neco jineho */
	
	var src = universalSource(co);
	drag_lock = 0;
	var type = drag_start.getAttribute("element_type");

	if ((type == TYPE_TABLE) || (type == TYPE_TITLE)) {
		/* pokud jsme hybali tabulkou, musime ukazat a aktualizovat relace */
		var number = drag_start.getAttribute("parent_number");
		for (var i=0;i<table_array[number].rows.length;i++) {
			if (table_array[number].rows[i]) {
				table_array[number].rows[i].updateRelations();
				table_array[number].rows[i].showRelations();
			}
		}
	}

	if (type == TYPE_ROWTITLE) {
		type = TYPE_ROW;
	}
	
	if (type == TYPE_ROW) {
		/* v tuto chvili vime, ze bylo pustene tlacitko predtim zmacknute na PRIMARY radce */
		var table_1 = parseInt(drag_start.getAttribute("parent_number"));
		var row_1 = parseInt(drag_start.getAttribute("row_number"));
		var tmp = get_exact_coords(co);
		x = tmp[0];
		y = tmp[1];
		/* 
			ted mame presne souradnice, kde byl mouseup.
			podivame se, jestli to neni 
				a) ta sama tabulka a jina radka
				b) jina tabulka
		*/
		tmp = get_target_tablerow(x,y);
		var table_2 = tmp[0];
		var row_2 = tmp[1];
		if (table_2 == -1) {
			/* nebylo to vubec na tabulce */
			drag_start = null;
			return;
		}
		if (table_2 != table_1 || row_1 != row_2) {
			/* jina tabulka nebo stejna tabulka a jina radka */
			
			/* stara tabulka fuck off */
			table_array[table_1].rows[row_1].deselect(); 
			table_array[table_1].deselect();
			table_admin.loseTable();
			
			var t1 = table_array[table_1]._title.innerHTML;
			var t2 = table_array[table_1].rows[row_1]._title.innerHTML;
			var newtitle = t2 + "_" + t1;
			var newtitle = t1 + "_" + t2; // foo_id instead of id_foo
			var row = table_array[table_2].addRow(newtitle,6);
			
			/* nova tabulka welcome */
			table_array[table_2].select();
			table_admin.manageTable(table_array[table_2]);
			row_admin.manageTable(table_array[table_2]);
			row_admin.manageRow(row);
			row.setFK();
                        /* row.setType("references "+table_1); */
			row.setType(table_array[table_1].rows[row_1].type);

			if (SQL_TYPES_SPEC[table_array[table_1].rows[row_1].type] == 1) {
				row.setSpec(table_array[table_1].rows[row_1].spec);
            }	
			row_2 = parseInt(row._div.getAttribute("row_number"));
			var relation = add_relation(table_1, row_1, table_2, row_2);
			relation.hide();
		}
	} /* if prvni element == radka */
	drag_start = null;

}


function global_event_mousemove(co) {
	if (drag_lock) {
		/* 
			nekdo hybnul s mysi a ma pritom zmackle tlacitko a zmacknul ho na pratelskem elementu
			=> bude posun
		*/
		var rel;
		var src = universalSource(co);
		var index = drag_start.getAttribute("parent_number");
		if (index != null) {
			var moving_elm = table_array[index]._div;
			var new_x = parseInt(moving_elm.style.left) + (co.clientX - mouse_x);
			var new_y = parseInt(moving_elm.style.top) + (co.clientY - mouse_y);
			table_array[index].moveTo(new_x,new_y);
			table_array[index].updateMini();
			mouse_x = co.clientX;
			mouse_y = co.clientY; 
		} else {
			/* necim hybeme, ale nema to parent number -> tak je to mapa */
			var moving_elm = document.getElementById("map_");
			var offs_x = co.clientX - mouse_x;
			var offs_y = co.clientY - mouse_y;
			var coef = DESK_SIZE / MAP_SIZE;
			window.scrollBy(coef * offs_x, coef * offs_y);
			mouse_x = co.clientX;
			mouse_y = co.clientY; 
			update_map_();
		}
	} 
}

function global_event_resize(co) {
	update_map_();
	update_bar();
}

function global_event_scroll(co) {
	update_map_();
	update_bar();
}

/* ------------------------------------------------------------------------------------ */

function get_target_tablerow(x, y) {
	var table=-1;
	var row=-1;
	var table_left, table_top, table_width, table_height;
	var row_left, row_top, row_width, row_height;
	/*
		pro dane souradnice vratime odpovidajici tabulku a radku. -1 pokud nee.
	*/
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i]) {
			table_left = parseInt(table_array[i]._div.style.left);
			table_top = parseInt(table_array[i]._div.style.top);
			table_width = parseInt(table_array[i]._div.offsetWidth);
			table_height = parseInt(table_array[i]._div.offsetHeight);
			if (x > table_left && x < table_left + table_width && y > table_top && y < table_top + table_height) {
				table = i;
			}
			for (var j=0;j<table_array[i].rows.length;j++) {
				if (table_array[i].rows[j]) {
					row_left = table_left + parseInt(table_array[i].rows[j]._div.offsetLeft);
					row_top = table_top + parseInt(table_array[i].rows[j]._div.offsetTop);
					row_width = parseInt(table_array[i].rows[j]._div.offsetWidth);
					row_height = parseInt(table_array[i].rows[j]._div.offsetHeight);
					if (x > row_left && x < row_left + row_width && y > row_top && y < row_top + row_height) {
						row = j;
					}
				} /* if not null */
			} /* for vsecky radky */ 
		} /* if not null */ 
	} /* for vsechny tabulky */
	return [table,row];
}

function add_table(x,y,title,custom_index) {
	var count = get_free_index(table_array);
	if (custom_index) {
		count = custom_index;
	}
	var max_zIndex = get_max_zIndex();
	var root=document.getElementById("root"); /* sem tabulku napojime */
	var table = new Table(x,y,count,max_zIndex+1,title); /* to je ona */
	table_array[count] = table; /* dame si objekt do pole */
	root.appendChild(table._div); /* a pridame i do HTML stromu */
	table.updateMini();
	raise_table(count);
	
	var bar = document.getElementById("bar");
	bar.style.zIndex = max_zIndex+2;
	var map = document.getElementById("map");
	map.style.zIndex = max_zIndex+2;
	return table;
}

function remove_table(index,no_animation) {
	for (var i=0;i<table_array[index].rows.length;i++) {
		if (table_array[index].rows[i]) {
			table_array[index].removeRow(i,no_animation);
		}
	}
	var endFuncRef = function() {
		table_array[index].destroy();
		table_array[index] = null;
		table_admin.loseTable();
		row_admin.loseRow();
		row_admin.loseTable();
	}
	if (no_animation) {
		endFuncRef();
	} else {
		animation_queue_add(endFuncRef);
	}
}

function add_relation(parent_1, row_1, parent_2, row_2) {
	/*
		pridani relace je narocne.
		a) vytvorime ji
		b) dame ji odkazy na rodice (4x)
		c) vlozime do DOM stromu
		d) pridame si na ni id do globalni tabulky relaci
		e) tohle id ji rekneme
		f) rekneme zucastnenym radkum, at si ji poznamenaji do svych poli
		
	*/

	var count = get_free_index(relation_array);
	var root=document.getElementById("root"); /* sem relaci napojime */
	var relation = new Relation(table_array[parent_1],
							        table_array[parent_1].rows[row_1],
								table_array[parent_2],
								table_array[parent_2].rows[row_2],
								count); /* to je ona */
	relation_array[count] = relation; /* dame si objekt do pole */
	root.appendChild(relation._div); /* a pridame i do HTML stromu */
	table_array[parent_1].rows[row_1].appendRelation(relation);
	table_array[parent_2].rows[row_2].appendRelation(relation);
	relation.update();
	return relation;
}

function remove_relation(index) {
	var parent_1 = relation_array[index].parent_1._div.getAttribute("parent_number");
	var parent_2 = relation_array[index].parent_2._div.getAttribute("parent_number");
	var row_1 = relation_array[index].row_1._div.getAttribute("row_number");
	var row_2 = relation_array[index].row_2._div.getAttribute("row_number");
	table_array[parent_2].rows[row_2].loseFK();
	table_array[parent_1].rows[row_1].removeRelation(index);
	table_array[parent_2].rows[row_2].removeRelation(index);
	relation_array[index].destroy(); /* odpojit z DOM */
	relation_array[index] = null; /* zrusit z globalni tabulky */
}

function reposition_tables() {
	/* maso :) */
	var avail_width = parseInt(document.body.clientWidth);
	var max_height=0, table_width, table_height;
	var actual_x=10, actual_y=10 + BAR_HEIGHT;
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i]) {
			table_width = parseInt(table_array[i]._div.offsetWidth);
			table_height = parseInt(table_array[i]._div.offsetHeight);
			if (actual_x + table_width > avail_width) {
				actual_x = 10;
				actual_y += 10 + max_height;
				max_height = 0;
			}
			table_array[i].moveTo(actual_x,actual_y);
			actual_x += 10 + table_width;
			if (table_height > max_height) {
				max_height = table_height;
			}
		}
	}
	
	for (var j=0;j<relation_array.length;j++) {
		if (relation_array[j]) {
			relation_array[j].update();
		}
	}
}

function clear_tables() {
	/* zrusi vsecko */
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i]) {
			remove_table(i,true);
		}
	}
}

function load(keyword) {

	table_admin = new TableAdmin();
	row_admin = new RowAdmin();
	io_admin = new IOAdmin();
	universalAttacher(document.body,"mousemove",global_event_mousemove); /* kvuli plynulemu posunu */
	universalAttacher(document.body,"mouseup",global_event_mouseup);     /* kvuli bugu v gecku pri mouseup */
	universalAttacher(document.body,"mousedown",global_event_mousedown); /* kvuli klikani na beton */
	universalAttacher(window,"keydown",global_event_scroll); /* kvuli mape */
	universalAttacher(window,"resize",global_event_resize); /* kvuli mape */
	universalAttacher(window,"scroll",global_event_scroll); /* kvuli mape */
	universalAttacher(window,"DOMMouseScroll",global_event_scroll); /* kvuli mape */	
	var elm = document.getElementById("root");
	elm.style.width = DESK_SIZE + "px";
	elm.style.height = DESK_SIZE + "px";
	elm.style.minHeight = DESK_SIZE + "px";
	
	elm = document.getElementById("bar");
	universalAttacher(elm,"mousedown",global_event_mousedown);
	elm.setAttribute("element_type",TYPE_BAR);
	elm.style.height = BAR_HEIGHT + "px";
	elm.appendChild(table_admin._div);
	
	elm = document.getElementById("shadow");
	elm.style.top = BAR_HEIGHT + "px";
	
	elm = document.getElementById("map");
	elm.style.width = MAP_SIZE + "px";
	elm.style.height = MAP_SIZE + "px";
	elm.setAttribute("element_type",TYPE_BAR);
	elm = document.getElementById("map_");
	elm.setAttribute("element_type",TYPE_MAP);

	update_bar();
	update_map_();
	
	elm = document.getElementById("row_type");
	var newopt, newoptgroup, total=0;
	for (var i=0;i<SQL_TYPES_DIVISION.length;i++) {
		newoptgroup = document.createElement("optgroup");
		newoptgroup.setAttribute("label",SQL_TYPES_DIVISION[i].name);
		newoptgroup.style.backgroundColor = SQL_TYPES_DIVISION[i].color;
		newoptgroup.setAttribute("element_type",TYPE_BAR);
		for (var j=0;j<SQL_TYPES_DIVISION[i].count;j++) {
			newopt = document.createElement("option");
			newopt.innerHTML = SQL_TYPES_DEFAULT[total];
			newopt.value = total;
			newopt.setAttribute("element_type",TYPE_BAR);
			total++;
			newoptgroup.appendChild(newopt);
		}
		elm.appendChild(newoptgroup);
	}


	/*****************************************/
	if (keyword == "") {
		
		add_table(100,120,"user");
		table_array[0].addRow("id",6); 
		table_array[0].rows[0].setPK();
		table_array[0].addRow("name",0);
		table_array[0].rows[1].setSpec(32);
		table_array[0].addRow("email",0);
		table_array[0].rows[2].setSpec(32);
		add_table(200,300,"address"); 
		table_array[1].addRow("id",6); 
		table_array[1].rows[0].setPK();
		table_array[1].addRow("user_id",6); 
		table_array[1].rows[1].setFK();
		table_array[1].rows[1].setIndex();
		table_array[1].addRow("street",0);
		table_array[1].rows[2].setSpec(32);
		table_array[1].addRow("state",0);
		table_array[1].rows[3].setSpec(2);
		table_array[1].addRow("zip",0);
		table_array[1].rows[4].setSpec(10);
		table_array[1].addRow("country",0);
		table_array[1].rows[5].setSpec(16);
		
		add_relation(0,0,1,1);
	} else {
		ajax_command(GET,"io.php?import=import&key="+encodeURIComponent(keyword),function(){return "";},import_xml);
		io_admin._key = keyword;
	}
}
