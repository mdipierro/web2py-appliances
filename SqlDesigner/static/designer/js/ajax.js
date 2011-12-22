/*
	ajax_command(method, target, data_func, return_func);
	ajax_manage(id, event, method, target, data_func, return_func);
*/

var GET = 1;
var POST = 2;

function ajax_command(method, target, data_func, return_func) {
	var xmlhttp = new XMLHTTP();
	var data = null; /* default - no data */
	var callback_response = function() {
		if (xmlhttp.getReadyState() == 4) {
			if (xmlhttp.getStatus() == 200) {
					return_func(xmlhttp.getResponseText());
			} else {
				xmlhttp.error("problem retrieving data");
			} 
		} /* response complete */
	} /* callback_response */
	xmlhttp.setResponse(callback_response);
	
	data = data_func(); /* request them from some user-specified routine */
	
	switch (method) {
		case GET:
			var newtarget = (/\?/.test(target) ? target+"&"+data : target+"?"+data);
			xmlhttp.open("GET",newtarget,true);
		break;
		case POST:
			xmlhttp.open("POST",target,true);
			xmlhttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
		break;
	} /* method */
	xmlhttp.send(data); /* off we go */
}

function ajax_manage(id, event, method, target, data_func, return_func) {
	var element = document.getElementById(id);
	if (!element) {
		alert("Element '"+id+"' not found");
		return;
	}
	if (method == POST && !XMLHTTP_supported()) {
		alert("IFRAME mode active -> POSTs not allowed");
		return;
	}
	var callback_request = function() {
		ajax_command(method,target,data_func,return_func);
	} /* callback_request */
	
	universalAttacher(element,event,callback_request);
}

function XMLHTTP_error(text) {
	alert('XMLHTTP error: "'+text+'", sorry...');
}

function XMLHTTP_open(method, target, async) {
	if (this.iframe) {
		this.temp_src = target;
	} else {
		this.obj.open(method, target, async);
	}
}

function XMLHTTP_send(data) {
	if (this.iframe) {
		this.ifr.src = this.temp_src;
	} else {
		this.obj.send(data);
	}
}

function XMLHTTP_setResponse(callback) {
	if (this.iframe) {
		universalAttacher(this.ifr,"load",callback);
	} else {
		this.obj.onreadystatechange = callback;
	}
}

function XMLHTTP_getResponseText() {
	if (this.iframe) {
		var data = this.ifr.contentWindow.document.body.innerHTML;
		/* uncomment this to save memory and confuse gecko: */
		/* this.ifr.parentNode.removeChild(this.ifr); */
		return data;
	} else {
		return this.obj.responseText;
	}
}

function XMLHTTP_getResponseXML() {
	if (this.iframe) {
		this.error("IFRAME mode active -> XML data not supported");
		return "";
	} else {
		return this.obj.responseXML;
	}
}

function XMLHTTP_getReadyState() {
	if (this.iframe) {
		return 4;
	} else {
		return this.obj.readyState;
	}
}

function XMLHTTP_getStatus() {
	if (this.iframe) {
		return 200;
	} else {
		return this.obj.status;
	}
}

function XMLHTTP_setRequestHeader(name,value) {
	if (!this.iframe) {
		this.obj.setRequestHeader(name,value);
	}
}

function XMLHTTP_isIframe() {
	return this.iframe;
}

function XMLHTTP() {
	this.iframe = false;
	this.open = XMLHTTP_open;
	this.send = XMLHTTP_send;
	this.error = XMLHTTP_error;
	this.setResponse = XMLHTTP_setResponse;
	this.getResponseText = XMLHTTP_getResponseText;
	this.getResponseXML = XMLHTTP_getResponseXML;
	this.getReadyState = XMLHTTP_getReadyState;
	this.getStatus = XMLHTTP_getStatus;
	this.setRequestHeader = XMLHTTP_setRequestHeader;
	this.isIframe = XMLHTTP_isIframe;
	this.obj = false;

	if (window.XMLHttpRequest) {
		/* gecko */
		this.obj = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		/* ie */
		this.obj = new ActiveXObject("Microsoft.XMLHTTP");
	}
	if (!this.obj) {
		/* no luck -> iframe */
		this.iframe = true;
		this.ifr = document.createElement("iframe");
		this.ifr.style.display = "none";
		this.ifr.src = "javascript:;";
		document.body.appendChild(this.ifr);
	}
}

function XMLHTTP_supported() {
	var dummy = new XMLHTTP();
	return (!dummy.isIframe());
}
