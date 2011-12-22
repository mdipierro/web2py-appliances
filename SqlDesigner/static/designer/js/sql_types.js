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

/* -------------------------- nase obecne datove typy ----------------------- */

var SQL_TYPES_DIVISION = [
	{color:"rgb(255,200,200)",name:"Character",count:5},
	{color:"rgb(238,238,170)",name:"Numeric",count:3},
	{color:"rgb(200,255,200)",name:"Date & Time",count:3}
];

var SQL_TYPES_DEFAULT = [
						"string",           /* 0 */
						"text",             /* 1 */
						"blob",             /* 2 */
						"password",         /* 3 */
						"upload",           /* 4 */
						"boolean",          /* 5 */
						"integer",          /* 6 */
						"double",           /* 7 */
						"datetime",         /* 8 */
						"date",             /* 9 */
						"time"              /* 10 */
];

var SQL_TYPES_VALUES = [
	/* defaultni hodnoty */
	"",
	"",
	"",
	"",
	"",
	"T",
	0,
	0.0,
	"1900-01-01 00:00:00",
	"1900-01-01",
	"00:00:00"
];

var SQL_TYPES_SPEC = [
	/* potrebuji-li doplnkovy inputbox */
	1,
        1,
	1,
	1,
	1,
	0,
	0,
	0,
	0,
	0,
	0
];
							
/* --------------------------- jejich ekvivalenty v sql ------------------ */
							
var SQL_TYPES_MYSQL = SQL_TYPES_DEFAULT;

/* --------------------------- fallback pro zname i nezname typy --------- */
						
var SQL_FALLBACK_MYSQL = new Object();
	SQL_FALLBACK_MYSQL["CHAR"] = 4;
	SQL_FALLBACK_MYSQL["VARCHAR"] = 4;
	SQL_FALLBACK_MYSQL["TINYTEXT"] = 5;
	SQL_FALLBACK_MYSQL["TEXT"] = 5;
	SQL_FALLBACK_MYSQL["BLOB"] = 7;
	SQL_FALLBACK_MYSQL["MEDIUMTEXT"] = 5;
	SQL_FALLBACK_MYSQL["MEDIUMBLOB"] = 7;
	SQL_FALLBACK_MYSQL["LONGTEXT"] = 5;
	SQL_FALLBACK_MYSQL["LONGBLOB"] = 7;
	SQL_FALLBACK_MYSQL["TINYINT"] = 1;
	SQL_FALLBACK_MYSQL["SMALLINT"] = 0;
	SQL_FALLBACK_MYSQL["MEDIUMINT"] = 0;
	SQL_FALLBACK_MYSQL["INT"] = 0;
	SQL_FALLBACK_MYSQL["INTEGER"] = 0;
	SQL_FALLBACK_MYSQL["BIGINT"] = 0;
	SQL_FALLBACK_MYSQL["FLOAT"] = 2;
	SQL_FALLBACK_MYSQL["DOUBLE"] = 3;
	SQL_FALLBACK_MYSQL["DECIMAL"] = 3;
	SQL_FALLBACK_MYSQL["DATE"] = 8;
	SQL_FALLBACK_MYSQL["TIME"] = 9;
	SQL_FALLBACK_MYSQL["DATETIME"] = 10;
	SQL_FALLBACK_MYSQL["TIMESTAMP"] = 11;
	SQL_FALLBACK_MYSQL["ENUM"] = 12;
	SQL_FALLBACK_MYSQL["SET"] = 13;
