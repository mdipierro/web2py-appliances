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
var animation_lock = 0; /* kolik prave bezi animaci */
var animation_end_queue = Array(); /* az skonci _posledni_ animace, tohle vsecko spustime */

function animation_queue_add(funcRef) {
	var i = get_free_index(animation_end_queue);
	animation_end_queue[i] = funcRef;
}

function animation_function(row_element,direction,endFunc) {
	var h = parseInt(row_element.style.height);
	h=h+direction;
	row_element.style.height = h+"px";
	
	if ((direction == 1 && h < ROW_HEIGHT) || (direction == -1 && h > 1)) {
		var funcRef = function() {
			animation_function(row_element,direction,endFunc);
		}
		setTimeout(funcRef,DELAY);
	} else {
		var funcRef = function() {
			end_animation(row_element,direction,endFunc);
		}
		setTimeout(funcRef,0);
	}
}

function start_animation(row_element,direction,endFunc) {
	animation_lock++;
	var number = parseInt(row_element.getAttribute("parent_number"));
	table_array[number].hideShadow();

	var h;
	if (direction == 1) {
		h = 1;
	}
	if (direction == -1) {
		h = ROW_HEIGHT;
	}
	row_element.style.height = h+ "px";
	var funcRef = function() {
		animation_function(row_element,direction,endFunc);
	}
	setTimeout(funcRef,DELAY);
}

function end_animation(row_element,direction,endFunc) {
	animation_lock--;
	if (endFunc) { /* na konci kazde animace muze neco byt */
		endFunc();
	}
	if (!animation_lock) { /* az skonci posledni animace, jeste neco pustime */
		for (var i=0;i<animation_end_queue.length;i++) {
			if (animation_end_queue[i]) {
				animation_end_queue[i]();
				animation_end_queue[i] = null;
			}
		}
	}
}
