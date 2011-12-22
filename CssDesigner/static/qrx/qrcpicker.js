/*
	Designed by J.Tabuchi <jun@jun.email.ne.jp>
	
	This software is distributed under "Common Public License".
	(see <http://www.eclipse.org/legal/cpl-v10.html> for detail infomation)
	
	http://www.qrone.org/
 */
/*
   
   ### SAMPLE ###
   
    <SCRIPT lang="JavaScript"><!--
	var cp = new QrColorPicker(defaultColor);
	cp.render();
	//--></SCRIPT>
   
   ---------------------------------------------------
	var cp = new QrColorPicker(defaultColor);
   
		// Create new ColorPicker Object.
   
	str = cp.getHTML();			// get HTML for inserting this Pulldown;
	cp.render();				// equals to document.write(p.getHTML());
	cp.set(value);				// set value.
	cp.get();					// get value.
	cp.onSelect = function(colorstr){};		// invoked when selecting color. called when mouse clicked.
	cp.onChange = function(colorstr){};		// invoked when previewing color. called every time mouse moved.
   
   ---------------------------------------------------
   <SCRIPT lang="JavaScript" src="qrx/qrcpicker.js"></SCRIPT>
   <SCRIPT lang="JavaScript" src="qrx/qrxpcom.js"></SCRIPT>
   
   link to the JavaScript code is needed for using.
 */

function QrColorPicker(_defaultColor){
	if(!_defaultColor) _defaultColor = "#FFFFFF";
	
	QrXPCOM.init();
	this.id = QrColorPicker.lastid++;
	this.defaultColor = _defaultColor;
	QrColorPicker.instanceMap["QrColorPicker"+this.id] = this;
}

QrColorPicker.prototype.getHTML = function(){
	var html = "<SPAN class=\"QrComponent\" id=\"$pickerId\" onclick=\"javascript:void(QrColorPicker.popupPicker('$pickerId'));\"><img src=\"qrx/transparentpixel.gif\" width=\"1\" height=\"1\" align=\"absmiddle\" id=\"$pickerId#color\" style=\"width:40px;height:20px;border:1px inset gray;background-color:\$defaultColor;cursor:pointer;\"/>\n<A href=\"javascript:void('QrColorPicker$pickerId');\"><SPAN id=\"$pickerId#text\">$defaultColor</SPAN></A></SPAN>\n<DIV style=\"display:none; position:absolute; border:solid 1px gray;background-color:white;z-index:2;\" id=\"$pickerId#menu\"\n onmouseout=\"javascript:QrColorPicker.restoreColor('$pickerId');\" onclick=\"javascript:QrXPCOM.onPopup();\">\n\n<NOBR><IMG SRC=\"qrx/colorpicker.jpg\" NATURALSIZEFLAG=\"3\" BORDER=\"0\" \nonMouseMove=\"javascript:QrColorPicker.setColor(event,'$pickerId');\"\nonClick=\"javascript:QrColorPicker.selectColor(event,'$pickerId');\" style=\"cursor:crosshair\"\nWIDTH=\"192\" HEIGHT=\"128\" ALIGN=\"BOTTOM\"><A HREF=\"http://www.qrone.org/\" TARGET=\"out\"><IMG SRC=\"qrx/lwllogo.jpg\" NATURALSIZEFLAG=\"3\" BORDER=\"0\" ALT=\"QrONE ColorPicker\"\nWIDTH=\"16\" HEIGHT=\"128\" ALIGN=\"BOTTOM\"></A></NOBR><BR><NOBR><IMG SRC=\"qrx/graybar.jpg\" NATURALSIZEFLAG=\"3\" BORDER=\"0\" \nonMouseMove=\"javascript:QrColorPicker.setColor(event,'$pickerId');\"\nonClick=\"javascript:QrColorPicker.selectColor(event,'$pickerId');\" style=\"cursor:crosshair\"\nWIDTH=\"192\" HEIGHT=\"8\" ALIGN=\"BOTTOM\"><IMG SRC=\"qrx/blank.jpg\" NATURALSIZEFLAG=\"3\" BORDER=\"0\"\nWIDTH=\"16\" HEIGHT=\"8\" ALIGN=\"BOTTOM\"></NOBR><BR>\n<NOBR><input type=\"text\" size=\"8\" id=\"$pickerId#input\" style=\"border:solid 1px gray;font-size:12pt;margin:1px;\" onkeyup=\"QrColorPicker.keyColor('$pickerId')\" value=\"$defaultColor\"/> <a href=\"javascript:QrColorPicker.transparent('$pickerId');\"><img src=\"qrx/grid.gif\" style=\"height:20px; width:20px;\" align=\"absmiddle\" border=\"0\">transparent</a></NOBR></DIV>";
	return html.replace(/\$pickerId/g,"QrColorPicker"+this.id).replace(/\$defaultColor/g,this.defaultColor);
}

QrColorPicker.prototype.render = function(){
	document.write(this.getHTML());
}

QrColorPicker.prototype.set = function(color){
	if(QrColorPicker.instanceMap["QrColorPicker"+this.id].onChange){
		QrColorPicker.instanceMap["QrColorPicker"+this.id].onChange(color);
	}
	if(color == "") color = "transparent";
	document.getElementById("QrColorPicker"+this.id+"#input").value = color;
	document.getElementById("QrColorPicker"+this.id+"#text").innerHTML = color;
	document.getElementById("QrColorPicker"+this.id+"#color").style.background = color;
}

QrColorPicker.prototype.get = function(){
	return document.getElementById("QrColorPicker"+this.id+"#input").value;
}

QrColorPicker.lastid = 0;

QrColorPicker.instanceMap = new Array;
QrColorPicker.restorePool = new Array;

QrColorPicker.transparent= function(id){
	QrColorPicker.instanceMap[id].set("transparent");
	document.getElementById(id+"#menu").style.display = "none";
	if(QrColorPicker.instanceMap[id].onChange){
		QrColorPicker.instanceMap[id].onChange("transparent");
	}
}

QrColorPicker.popupPicker= function(id){
	var pop = document.getElementById(id);
	var p = QrXPCOM.getDivPoint(pop);
	QrXPCOM.setDivPoint(document.getElementById(id+"#menu"), p.x, p.y+ 20);
	
	document.getElementById(id+"#menu").style.display = "";
	QrXPCOM.onPopup(document.getElementById(id+"#menu"));
}

QrColorPicker.setColor = function(event,id){
	if(!QrColorPicker.restorePool[id]) QrColorPicker.restorePool[id] = document.getElementById(id+"#input").value;
	
	var d = QrXPCOM.getMousePoint(event,document.getElementById(id+"#menu"));
	var picked = QrColorPicker.colorpicker(d.x,d.y).toUpperCase();
	
	document.getElementById(id+"#input").value = picked;
	document.getElementById(id+"#text").innerHTML = picked;
	document.getElementById(id+"#color").style.background = picked;
	if(QrColorPicker.instanceMap[id].onChange){
		QrColorPicker.instanceMap[id].onChange(picked);
	}
	return picked;
};


QrColorPicker.keyColor = function(id){
	try{
		document.getElementById(id+"#color").style.background = document.getElementById(id+"#input").value;
		QrColorPicker.restorePool[id] = document.getElementById(id+"#input").value;
		document.getElementById(id+"#text").innerHTML = QrColorPicker.restorePool[id];
	}catch(e){}
};


QrColorPicker.selectColor = function(event,id){
	var picked = QrColorPicker.setColor(event,id);
	
	document.getElementById(id+"#menu").style.display = "none";
	QrColorPicker.restorePool[id] = picked;
	if(QrColorPicker.instanceMap[id].onSelect){
		QrColorPicker.instanceMap[id].onSelect(picked);
	}
};

QrColorPicker.restoreColor = function(id){
	if(QrColorPicker.restorePool[id]){
		document.getElementById(id+"#input").value = QrColorPicker.restorePool[id];
		document.getElementById(id+"#text").innerHTML = QrColorPicker.restorePool[id];
		document.getElementById(id+"#color").style.background = QrColorPicker.restorePool[id];
		if(QrColorPicker.instanceMap[id].onChange){
			QrColorPicker.instanceMap[id].onChange(QrColorPicker.restorePool[id]);
		}
		QrColorPicker.restorePool[id] = null;
	}
};

QrColorPicker.colorpicker = function(prtX,prtY){
	var colorR = 0;
	var colorG = 0;
	var colorB = 0;
	
	if(prtX < 32){
		colorR = 256;
		colorG = prtX * 8;
		colorB = 1;
	}
	if(prtX >= 32 && prtX < 64){
		colorR = 256 - (prtX - 32 ) * 8;
		colorG = 256;
		colorB = 1;
	}
	if(prtX >= 64 && prtX < 96){
		colorR = 1;
		colorG = 256;
		colorB = (prtX - 64) * 8;
	}
	if(prtX >= 96 && prtX < 128){
		colorR = 1;
		colorG = 256 - (prtX - 96) * 8;
		colorB = 256;
	}
	if(prtX >= 128 && prtX < 160){
		colorR = (prtX - 128) * 8;
		colorG = 1;
		colorB = 256;
	}
	if(prtX >= 160){
		colorR = 256;
		colorG = 1;
		colorB = 256 - (prtX - 160) * 8;
	}
	
	if(prtY < 64){
		colorR = colorR + (256 - colorR) * (64 - prtY) / 64;
		colorG = colorG + (256 - colorG) * (64 - prtY) / 64;
		colorB = colorB + (256 - colorB) * (64 - prtY) / 64;
	}
	if(prtY > 64 && prtY <= 128){
		colorR = colorR - colorR * (prtY - 64) / 64;
		colorG = colorG - colorG * (prtY - 64) / 64;
		colorB = colorB - colorB * (prtY - 64) / 64;
	}
	if(prtY > 128){
		colorR = 256 - ( prtX / 192 * 256 );
		colorG = 256 - ( prtX / 192 * 256 );
		colorB = 256 - ( prtX / 192 * 256 );
	}
	
	colorR = parseInt(colorR);
	colorG = parseInt(colorG);
	colorB = parseInt(colorB);
	
	if(colorR >= 256){
		colorR = 255;
	}
	if(colorG >= 256){
		colorG = 255;
	}
	if(colorB >= 256){
		colorB = 255;
	}
	
	colorR = colorR.toString(16);
	colorG = colorG.toString(16);
	colorB = colorB.toString(16);
	
	if(colorR.length < 2){
	colorR = 0 + colorR;
	}
	if(colorG.length < 2){
	colorG = 0 + colorG;
	}
	if(colorB.length < 2){
	colorB = 0 + colorB;
	}
	
	return "#" + colorR + colorG + colorB;
}