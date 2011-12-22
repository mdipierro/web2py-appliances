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

var reposition = 0;

function import_xml_relation(relation) {
	var table_1 = relation.match(/<table_1>([^<]*)<\/table_1>/);
	var table_2 = relation.match(/<table_2>([^<]*)<\/table_2>/);
	var row_1 = relation.match(/<row_1>([^<]*)<\/row_1>/);
	var row_2 = relation.match(/<row_2>([^<]*)<\/row_2>/);
	add_relation(table_1[1],row_1[1],table_2[1],row_2[1]);
}

function import_xml_row(table, row) {
	var r;
	var head = row.match(/<row[^>]*>/);
	var id = head[0].match(/id="([^"]*)"/);

	var title = row.match(/<title>([^<]*)<\/title>/);
	var stype = row.match(/<type>([^<]*)<\/type>/);
	var type=13; /* default -> UNKNOWN */
	for (var i=0;i<SQL_TYPES_DEFAULT.length;i++) {
		if (stype[1].toLowerCase() == SQL_TYPES_DEFAULT[i].toLowerCase()) {
			type = i;
		}
	}
	
	if (id) {
		r=table.addRow(title[1],type,id[1]);
	} else {
		r=table.addRow(title[1],type);
	}

	var def = row.match(/<default>([^<]*)<\/default>/);
	r.setDef(def[1]);
	var index = head[0].match(/index="[^"]*"/);
	if (index) {
		r.setIndex();
	}
	var pk = head[0].match(/pk="[^"]*"/);
	if (pk) {
		r.setPK();
	}
	var fk = head[0].match(/fk="[^"]*"/);
	if (fk) {
		r.setFK();
	}
	var nn = head[0].match(/nn="[^"]*"/);
	if (nn) {
		r.setNN();
	}
	var spec = head[0].match(/special="([^"]*)"/);
	if (spec) {
		r.setSpec(spec[1]);
	}
}


function import_xml_table(table) {
	var t;
	var pos_x=0;
	var pos_y=0;
	var head = table.match(/<table[^>]*>/);
	var id = head[0].match(/id="([^"]*)"/);
	var title = head[0].match(/title="([^"]*)"/);
	var x = head[0].match(/x="([^"]*)"/);
	var y = head[0].match(/y="([^"]*)"/);
	if (x) { pos_x = x[1]; } else { reposition = 1;}
	if (y) { pos_y = y[1]; } else { reposition = 1;}
	if (id) {
		t = add_table(pos_x,pos_y,title[1],id[1]);
	} else {
		t = add_table(pos_x,pos_y,title[1]);
	}
	var rows = table.match(/<row[^>]*>.*?<\/row>/g);
	for (var i=0;i<rows.length;i++) {
		import_xml_row(t,rows[i]);
	}
}

function import_xml(data) {
	/* nacte data z drive ulozeneho souboru */
	

	/* zadne newliny, delaji bordel */
	data = data.replace(/[\n\r]/g,'');
	
	/* jen vnitrek globalniho tagu <sql> */
	var clear = data.match(/<sql>(.*)<\/sql>/); 
	if (!clear) {
		alert('No data!');
		return;
	}

	/* vsechno vycistime */
	clear_tables();

	/* a jedeme - tabulky */
	var tables = clear[1].match(/<table[^>]*>.*?<\/table>/g);
	for (var i=0;i<tables.length;i++) {
		import_xml_table(tables[i]);
	}
	
	/* vposled relace */
	var relations = clear[1].match(/<relation[^>]*>.*?<\/relation>/g);
	if (relations) {
		for (var i=0;i<relations.length;i++) {
			import_xml_relation(relations[i]);
		}
	}
	
	if (reposition) {
		animation_queue_add(reposition_tables);
		reposition = 0;
	}
}

function export_xml() {
	/* 
		vyexportuje data do xml souboru. priklad:
	
	<?xml version="1.0" ?>
	<!-- WWWSQLEditor XML export -->
	<sql>
		<table id="3" title="tabulka" x="30" y="50">
			<row id="0" pk="pk">
				<default>0</default>
				<title>id</title>
				<type>Integer</type>
			</row>
			<row id="1" index="index" fk="fk">
				<type>Integer</type>
				<default>0</default>
				<title>id_neco</title>
			</row>
			<row id="2" nn="nn" special="64">
				<type>String</type>
				<title>hodnota</title>
			</row>
		<table>
		<relation>
			<table_1>3</table_1>
			<table_2>4</table_2>
			<row_1>0</row_1>
			<row_2>0</row_2>
		</relation>
	</sql>	
	*/
	
	/* hlavicka */
	var x,y;
	var str, row;
	var data = '<?xml version="1.0" ?>\n';
	data += '<!-- WWWSQLEditor XML export -->\n';
	data += '<sql>\n';
	
	/* tabulky a radky */
	for (var i=0;i<table_array.length;i++) {
		if (table_array[i]) {
			x = parseInt(table_array[i]._div.style.left);
			y = parseInt(table_array[i]._div.style.top);
                        title=table_array[i]._title.innerHTML;
			data += '\t<table id="'+i+'" title="'+title+'" x="'+x+'" y="'+y+'" >\n';
			for (var j=0;j<table_array[i]._rows.childNodes.length;j++) {
				var id = table_array[i]._rows.childNodes[j].getAttribute("row_number");
				row = table_array[i].rows[id];
				str = 'id="'+id+'"';
				if (row.pk) { /* primary key */
					str += ' pk="pk"';
				}
				if (row.fk) { /* foreign key */
					str += ' fk="fk"';
				}
				if (row.index) { /* index */
					str += ' index="index"';
				}
				if (row.nn) { /* primary key */
					str += ' nn="nn"';
				}
				if (SQL_TYPES_SPEC[row.type]) { /* spec */
					str += ' special="'+row.spec+'"';
				}
				data += '\t\t<row '+str+'>\n';
				data += '\t\t\t<title>'+row._title.innerHTML+'</title>\n';
				data += '\t\t\t<default>'+row.def+'</default>\n';
                                rtype=SQL_TYPES_DEFAULT[row.type]
                                if(row.fk) {
	for (var k=0;k<relation_array.length;k++) {
		if (relation_array[k]) {
			table_1 = relation_array[k].parent_1.number;
			table_2 = relation_array[k].parent_2.number;
			row_1 = relation_array[k].row_1._div.getAttribute("row_number");
			row_2 = relation_array[k].row_2._div.getAttribute("row_number");
                        if(table_2==i && row_2==id) rtype="reference "+table_array[table_1]._title.innerHTML;
} 
}

                                }
				data += '\t\t\t<type>'+rtype+'</type>\n';
				data += '\t\t</row>\n';
			} /* pro vsechny radky */
			data += '\t</table>\n';
		} /* pokud tabulka existuje */
	} /* pro vsechny tabulky */
	
	/* relace */
	var table_1, table_2, row_1, row_2;
	for (var k=0;k<relation_array.length;k++) {
		if (relation_array[k]) {
			table_1 = relation_array[k].parent_1.number;
			table_2 = relation_array[k].parent_2.number;
			row_1 = relation_array[k].row_1._div.getAttribute("row_number");
			row_2 = relation_array[k].row_2._div.getAttribute("row_number");
			data += '\t<relation>\n';
			data += '\t\t<table_1>'+table_1+'</table_1>\n';
			data += '\t\t<row_1>'+row_1+'</row_1>\n';
			data += '\t\t<table_2>'+table_2+'</table_2>\n';
			data += '\t\t<row_2>'+row_2+'</row_2>\n';
			data += '\t</relation>\n';
		}
	}
	
	/* paticka */
	data += '</sql>';
	return data;
}


function io_show(import_btn) {
	var btn = document.getElementById("import");
	if (import_btn) {
		btn.style.display = "block";
	} else {
		btn.style.display = "none";
	}
	var area = document.getElementById("area");
	area.parentNode.style.display = "block";
}