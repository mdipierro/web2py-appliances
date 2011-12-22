/*
	Designed by J.Tabuchi <jun@jun.email.ne.jp>
	
	This software is distributed under "Common Public License".
	(see <http://www.eclipse.org/legal/cpl-v10.html> for detail infomation)
	
	http://www.qrone.org/
 */

function setCookie(sName, sValue){
	date = new Date();
	date.setMonth( date.getMonth() + 1 );
	document.cookie = sName + "=" + encodeURI(escape(sValue)) 
		+ "; expires=" + date.toGMTString();
}

function getCookie(sName){
	var aCookie = document.cookie.split("; ");
	for (var i=0; i < aCookie.length; i++){
		var aCrumb = aCookie[i].split("=");
		if (sName == aCrumb[0]) return decodeURI(aCrumb[1]);
	}
	return null;
}


function ListDiv(_id){
	var base_id = _id;
	var id_array = new Array;
	var div_array = new Array;
	
	this.append = function(id, html){
		div_array[id] = "<div id='" + base_id +"::"+ id + "'>" + html + "</div>";
		id_array.push(id);
		
		document.getElementById(base_id).innerHTML += div_array[id];
	}
	
}

function TabbedDiv(_id){
	
}


//------------------------------

QrXPCOM.init = function(){
	if(QrXPCOM.inited) return;
	QrXPCOM.documentBodyOnClickOld = document.body.onclick;
	document.body.onclick = function(event){
		if(QrXPCOM.documentBodyOnClickOld) QrXPCOM.documentBodyOnClickOld();
		id="id5";
		if(QrXPCOM.popupblock == false && QrXPCOM.popup){
			QrXPCOM.popup.style.display = "none";
		}else{
			QrXPCOM.popupblock = false;
		}
	}
	QrXPCOM.inited = true;
}

QrXPCOM.popupblock;
QrXPCOM.onPopup = function(popup){
	if(popup){
		if(QrXPCOM.popup && QrXPCOM.popup != popup) QrXPCOM.popup.style.display = "none";
		QrXPCOM.popup = popup;
	}
	QrXPCOM.popupblock = true;
}



QrXPCOM.Enter		 = 13;
QrXPCOM.LeftArrow	 = 37;
QrXPCOM.UpArrow		 = 38;
QrXPCOM.RightArrow	 = 39;
QrXPCOM.DownArrow	 = 40;

function QrXPCOM(){}
function QrPoint(_x,_y){
	this.x = _x;
	this.y = _y;
}

function QrDimension(_width,_height){
	this.width = _width;
	this.height = _height;
}


QrXPCOM.isIE = function(){
	return window.ActiveXObject;
}

QrXPCOM.isImageFile = function(src){
	if(  src.substring(src.lastIndexOf(".")).toLowerCase() == ".gif"
	  || src.substring(src.lastIndexOf(".")).toLowerCase() == ".jpg"
	  || src.substring(src.lastIndexOf(".")).toLowerCase() == ".bmp"
	  || src.substring(src.lastIndexOf(".")).toLowerCase() == ".jpeg"
	  || src.substring(src.lastIndexOf(".")).toLowerCase() == ".png"){
		return true;
	}else{
		return false;
	}
}


QrXPCOM.getEventKeyCode = function(e){
	if(QrXPCOM.isIE()){
		return event.keyCode;
	}else{
		return e.keyCode;
	}
}

QrXPCOM.onShift = function(e){
	if(QrXPCOM.isIE()) return event.shiftKey;
	else{
		return e.shiftKey;
	}
}


QrXPCOM.getMousePointForDrag = function(e){
	if(QrXPCOM.isIE()){
		return new QrPoint(event.clientX + document.body.scrollLeft,event.clientY + document.body.scrollTop);
	}else{
		return new QrPoint(e.clientX + document.body.scrollLeft,e.clientY + document.body.scrollTop);
	}
}

QrXPCOM.getMousePoint = function(e,div){
	if(div){
		var da = QrXPCOM.getMousePoint(e);
		var db = QrXPCOM.getDivPoint(div);
		return new QrPoint(da.x-db.x,da.y-db.y);
	}
	
	if(QrXPCOM.isIE()){
		var p = QrXPCOM.getDivPoint(event.srcElement);
		return new QrPoint(p.x+ event.offsetX,p.y + event.offsetY);
	}else{
		return new QrPoint(e.pageX,e.pageY);
		//return new QrPoint(e.clientX + document.body.scrollLeft,e.clientY + document.body.scrollTop);
	}
}

QrXPCOM.setDivPoint = function(div, x, y){
	div.style.top  = y + "px";
	div.style.left = x + "px";
}


QrXPCOM.getDivPoint = function(div){
	if(div.style && (div.style.position == "absolute" || div.style.position == "relative")){
		return new QrPoint(div.offsetLeft+1, div.offsetTop+1);
	}else if(div.offsetParent){
		var d = QrXPCOM.getDivPoint(div.offsetParent);
		return new QrPoint(d.x+div.offsetLeft, d.y+div.offsetTop);
	}else{
		return new QrPoint(0,0);
	}
}


QrXPCOM.getDivSize = function(div){
	if(QrXPCOM.isIE()){
		return new QrDimension(div.offsetWidth,div.offsetHeight);
	}else{
		return new QrDimension(div.offsetWidth-2,div.offsetHeight-2);
	}
}

QrXPCOM.setDivSize = function(div, x, y){
	div.style.width  = x + "px";
	div.style.height = y + "px";
}


QrXPCOM.getBodySize = function(){
	return new QrDimension(document.body.clientWidth,document.body.clientHeight);
}