/*
	Designed by J.Tabuchi <jun@jun.email.ne.jp>
	
	This software is distributed under "Common Public License".
	(see <http://www.eclipse.org/legal/cpl-v10.html> for detail infomation)
	
	http://www.qrone.org/
 */
/*
   
   ### SAMPLE ###
   
   <SCRIPT lang="JavaScript"><!--
   var pl = new QrSpinner();
   pl.render();
   //--></SCRIPT>
   
   ---------------------------------------------------
   var p = new QrSpinner(_defaultValue, _defaultSize, _name);
   
   		// Create QrPulldown Object. Any parameters may not be specified.
   		// <input value="_defaultValue" size="_defaultSize" name="_name"/>
   		
   
   str = p.getHTML();		// get HTML for inserting this Pulldown;
   p.render();				// equals to document.write(p.getHTML());
   p.set(value);			// set value.
   p.get();					// get value.
   
   ---------------------------------------------------
   <SCRIPT lang="JavaScript" src="qrx/qrcspinner.js"></SCRIPT>
   <SCRIPT lang="JavaScript" src="qrx/qrxpcom.js"></SCRIPT>
   
   link to the JavaScript code is needed for using.
 */

function QrSpinner(_defaultValue, _defaultSize, _Name){
	if(!_defaultValue) _defaultValue = "";
	if(!_defaultSize)  _defaultSize  = "4";
	if(!_Name)  _Name  = " name=\""+_Name+"\" ";
	else _Name = "";
	
	this.id = QrSpinner.lastId++;
	this.defaultValue = _defaultValue;
	this.defaultSize  = _defaultSize;
	this.name = _Name;
	
	QrSpinner.instanceMap["QrSpinner"+this.id] = this;
}

QrSpinner.prototype.getHTML = function(){
	var html =  "<span class=\"QrSpinner\" style=\"padding:1px\"><input id=\"$spinnerId#input\" style=\"height:22px;padding-left:2px;$IEPoint\" size=\"$defaultSize\" value=\"$defaultValue\" onkeyup=\"QrSpinner.onKeyup('$spinnerId')\" $NamePoint/><span class=\"QrSpinnerImg\" style=\"margin-left:2px;position:relative;z-index:0;\"><img src=\"qrx/spinner-normal.gif\" align=\"top\" height=\"22\" id=\"$spinnerId#button\" onmousemove=\"QrSpinner.onHover(event,'$spinnerId')\" onmouseout=\"QrSpinner.onOut(event,'$spinnerId')\" onmousedown=\"QrSpinner.onDown(event,'$spinnerId')\"></span></span>";
	if(QrXPCOM.isIE()) html=html.replace(/\$IEPoint/,"margin-top:-1px;");
	else html=html.replace(/\$IEPoint/,"");
	return html.replace(/\$spinnerId/g,"QrSpinner"+this.id)
			   .replace(/\$defaultSize/g,this.defaultSize)
			   .replace(/\$defaultValue/g,this.defaultValue)
			   .replace(/\$NamePoint/g,this.name);
}

QrSpinner.prototype.render = function(){
	document.write(this.getHTML());
}

QrSpinner.prototype.set = function(value){
	document.getElementById("QrSpinner"+this.id+"#input").value = value;
	if(QrSpinner.instanceMap["QrSpinner"+this.id].onChange){
		QrSpinner.instanceMap["QrSpinner"+this.id].onChange(value);
	}
}

QrSpinner.prototype.get = function(){
	return document.getElementById("QrSpinner"+this.id+"#input").value;
}

QrSpinner.lastId = 0;
QrSpinner.instanceMap = new Array;

QrSpinner.onHover = function(e, id){
	var p = QrXPCOM.getMousePoint(e);
	var d = QrXPCOM.getDivPoint(document.getElementById(id+"#button"));
	
	if((p.y - d.y)<10){
		document.getElementById(id+"#button").src = "qrx/spinner-updown.gif";
	}
	if((p.y - d.y)>10){
		document.getElementById(id+"#button").src = "qrx/spinner-downdown.gif";
	}
}

QrSpinner.onOut = function(e, id){
	document.getElementById(id+"#button").src = "qrx/spinner-normal.gif";
}


QrSpinner.onKeyup = function(id){
	if(QrSpinner.instanceMap[id].onChange){
		QrSpinner.instanceMap[id].onChange(document.getElementById(id+"#input").value);
	}
}

QrSpinner.onDown = function(e, id){
	var p = QrXPCOM.getMousePoint(e);
	var d = QrXPCOM.getDivPoint(document.getElementById(id+"#button"));
	
	var v = parseInt(document.getElementById(id+"#input").value);
	if(!v) v = 0;
	if((p.y - d.y)<10){
		document.getElementById(id+"#input").value = ++v;
	}
	if((p.y - d.y)>10){
		document.getElementById(id+"#input").value = --v;
	}
	if(QrSpinner.instanceMap[id].onChange){
		QrSpinner.instanceMap[id].onChange(v);
	}
}