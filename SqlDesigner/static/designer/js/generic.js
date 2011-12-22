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

function get_free_index(arr) {
	var index = -1;
	for (var i=0;i<arr.length;i++) {
		if (index == -1 && !arr[i]) {
			index = i;
		}
	}
	return (index == -1 ? arr.length : index);
}

function dd(variable) {
	var msg="";
	for (property in variable) {
		if (typeof(variable[property]) != "function") {
			msg += property+": "+variable[property]+"\n";
		}
	}
	alert(msg);
}

function universalAttacher(element, event, callback) {
	if (element.addEventListener) {
		/* gecko */
		element.addEventListener(event,callback,false);
	} else if (element.attachEvent) {
		/* ie */
		element.attachEvent("on"+event,callback);
	} else {
		/* ??? */
		element["on"+event] = callback;
	}
	
}

function universalSource(event) {
	return (event.target ? event.target : event.srcElement);
}

function get_exact_coords(event) {
	var x,y;
	if (event.pageX) {
		/* gecko */
		x = event.pageX;
		y = event.pageY;
	} else {
		/* ie */
		x = event.clientX + document.body.scrollLeft;
		y = event.clientY + document.body.scrollTop;
	}
	return [x,y];
}