/*
	Designed by J.Tabuchi <jun@jun.email.ne.jp>
	
	This software is distributed under "Common Public License".
	(see <http://www.eclipse.org/legal/cpl-v10.html> for detail infomation)
	
	http://www.qrone.org/
 */
/*
   
   ### SAMPLE ###
   
   <SCRIPT lang="JavaScript"><!--
   var pl = new QrPulldown();
   pl.addItem("item1","item1value");
   pl.addItem("item2","item2value");
   pl.addItem("item3","item3value");
   pl.render();
   //--></SCRIPT>
   
   ---------------------------------------------------
   var p = new QrPulldown(_defaultValue, _defaultSize, _name);
   
   		// Create QrPulldown Object. Any parameters may not be specified.
   		// <input value="_defaultValue" size="_defaultSize" name="_name"/>
   		
   
   str = p.getHTML();		// get HTML for inserting this Pulldown;
   p.render();				// equals to document.write(p.getHTML());
   p.set(value);			// set value.
   p.get();					// get value.
   p.addItem(html,value);	// add new Item for this pulldown
   
   
   ---------------------------------------------------
   <SCRIPT lang="JavaScript" src="qrx/qrcpulldown.js"></SCRIPT>
   <SCRIPT lang="JavaScript" src="qrx/qrxpcom.js"></SCRIPT>
   <link rel="stylesheet" type="text/css" href="qrx/qrpulldown.css">
   
   link to BOTH the JavaScript code AND the CSS style sheet is needed for using.
 */

function QrPulldown(_defaultValue, _defaultSize, _Name){
	if(!_defaultValue) _defaultValue = "";
	if(!_defaultSize)  _defaultSize  = "16";
	if(!_Name)  _Name  = " name=\""+_Name+"\" ";
	else _Name = "";
	
	QrXPCOM.init();
	this.itemLastId = 0;
	this.id = QrPulldown.lastid++;
	this.itemHtml = "";
	this.defaultValue = _defaultValue;
	this.defaultSize  = _defaultSize;
	this.name = _Name;
	
	QrPulldown.instanceMap["QrPulldown"+this.id] = this;
}

QrPulldown.prototype.getHTML = function(){
	var html = "<nobr><span class=\"QrPulldown\" id=\"$pulldownId\"><input class=\"QrPulldownInput\" value=\"$defaultValue\" id=\"$pulldownId#input\" size=\"$defaultSize\" onkeyup=\"QrPulldown.onKeyup('$pulldownId');\" $NamePoint$IEPoint/><span id=\"$pulldownId#button\" class=\"QrPulldownButton\" onmousedown=\"QrPulldown.onClick('$pulldownId');\"><img src=\"qrx/pulldown-normal.gif\" align=\"top\" height=\"22\" id=\"$pulldownId#img\" onmouseover=\"QrPulldown.onButtonHover('$pulldownId');\" onmouseout=\"QrPulldown.onButtonOut('$pulldownId');\"></span></span></nobr>\n<DIV class=\"QrPulldownMenu\" style=\"display:none;\" id=\"$pulldownId#menu\" onclick=\"QrXPCOM.onPopup();\"><DIV style=\"margin:2px;\" id=\"$pulldownId#menuinner\">\n</DIV></DIV>";
	if(QrXPCOM.isIE()) html=html.replace(/\$IEPoint/,"style=\"margin-top:-1px\"");
	else html=html.replace(/\$IEPoint/,"");;
	
	return html.replace(/\$pulldownId/g,"QrPulldown"+this.id)
			   .replace(/\$defaultSize/g,this.defaultSize)
			   .replace(/\$defaultValue/g,this.defaultValue)
			   .replace(/\$NamePoint/g,this.name);
}

QrPulldown.prototype.render = function(){
	document.write(this.getHTML());
	//this.after();
}

QrPulldown.prototype.set = function(value){
	document.getElementById("QrPulldown"+this.id+"#input").value = value;
	if(QrPulldown.instanceMap["QrPulldown"+this.id].onChange){
		QrPulldown.instanceMap["QrPulldown"+this.id].onChange(value);
	}
}

QrPulldown.prototype.get = function(){
	return document.getElementById("QrPulldown"+this.id+"#input").value;
}


QrPulldown.prototype.addItem = function (html,value){
	var thisid = this.itemLastId++;
	var cashhtml = "<DIV class=\"QrPulldownItem\" id=\"$pulldownId#item$itemId\" onmouseover=\"QrPulldown.onHover('$pulldownId', '$pulldownId#item$itemId', '$value');\" onmouseout=\"QrPulldown.onOut('$pulldownId', '$pulldownId#item$itemId');\" onclick=\"QrPulldown.onSelect('$pulldownId','$value');\">$html</DIV>";
	cashhtml = cashhtml.replace(/\$pulldownId/g,"QrPulldown"+this.id).replace(/\$itemId/g,thisid).replace(/\$html/g,html).replace(/\$value/g,value);
	
	this.itemHtml += cashhtml;
	document.getElementById("QrPulldown"+this.id+"#menuinner").innerHTML = this.itemHtml;
}


QrPulldown.lastid = 0;
QrPulldown.instanceMap = new Array;

QrPulldown.onOut = function(id, itemid){
	if(document.getElementById(itemid).className == "QrPulldownItemHover"){
		document.getElementById(itemid).className = "QrPulldownItem";
	}
	if(QrPulldown.instanceMap[id].onChange){
		QrPulldown.instanceMap[id].onChange(document.getElementById(id+"#input").value);
	}
}

QrPulldown.onHover = function(id, itemid, value){
	if(document.getElementById(itemid).className == "QrPulldownItem"){
		document.getElementById(itemid).className = "QrPulldownItemHover";
	}
	if(QrPulldown.instanceMap[id].onChange){
		QrPulldown.instanceMap[id].onChange(value);
	}
}

QrPulldown.onButtonOut = function(id){
	document.getElementById(id+"#img").src = "qrx/pulldown-normal.gif";
}

QrPulldown.onButtonHover = function(id){
	document.getElementById(id+"#img").src = "qrx/pulldown-down.gif";
}

QrPulldown.onClick = function(id){
	var p = QrXPCOM.getDivPoint(document.getElementById(id));
	var r = QrXPCOM.getDivSize(document.getElementById(id));
	if(QrXPCOM.isIE()) QrXPCOM.setDivPoint(document.getElementById(id+"#menu"), p.x+1, p.y+ 22);
	else QrXPCOM.setDivPoint(document.getElementById(id+"#menu"), p.x+1, p.y+ 22-1);
	
	document.getElementById(id+"#menu").style.display = "";
	QrXPCOM.onPopup(document.getElementById(id+"#menu"));
}

QrPulldown.onKeyup = function(id){
	if(QrPulldown.instanceMap[id].onChange){
		QrPulldown.instanceMap[id].onChange(document.getElementById(id+"#input").value);
	}
}

QrPulldown.onSelect = function(id, value){
	document.getElementById(id+"#input").value = value;
	document.getElementById(id+"#menu").style.display = "none";
	
	if(QrPulldown.instanceMap[id].onSelect){
		QrPulldown.instanceMap[id].onSelect(value);
	}
	if(QrPulldown.instanceMap[id].onChange){
		QrPulldown.instanceMap[id].onChange(value);
	}
}