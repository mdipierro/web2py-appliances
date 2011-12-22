	//replace tabulation by the good number of white spaces
	EditArea.prototype.replace_tab= function(text){
		return text.replace(/((\n?)([^\t\n]*)\t)/gi, editArea.smartTab);		// slower than simple replace...	
	};
	
	// call by the replace_tab function
	EditArea.prototype.smartTab= function(){
		val="                   ";
		return EditArea.prototype.smartTab.arguments[2] + EditArea.prototype.smartTab.arguments[3] + val.substr(0, editArea.tab_nb_char - (EditArea.prototype.smartTab.arguments[3].length)%editArea.tab_nb_char);
	};
	
	EditArea.prototype.add_style= function(styles){
		if(styles.length>0){
			newcss = document.createElement("style");
			newcss.type="text/css";
			newcss.media="all";
			document.getElementsByTagName("head")[0].appendChild(newcss);
			cssrules = styles.split("}");
			newcss = document.styleSheets[0];
			if(newcss.rules) { //IE
				for(i=cssrules.length-2;i>=0;i--) {
					newrule = cssrules[i].split("{");
					newcss.addRule(newrule[0],newrule[1])
				}
			}
			else if(newcss.cssRules) { //Firefox etc
				for(i=cssrules.length-1;i>=0;i--) {
					if(cssrules[i].indexOf("{")!=-1){
						newcss.insertRule(cssrules[i]+"}",0);
					}
				}
			}
		}
	};
	
	EditArea.prototype.set_font= function(family, size){
		var elems= new Array("textarea", "content_highlight", "cursor_pos", "end_bracket", "selection_field", "line_number");
		if(family && family!="")
			this.settings["font_family"]= family;
		if(size && size>0)
			this.settings["font_size"]=size;
		if(this.nav['isOpera'])	// opera can't manage non monospace font
			this.settings['font_family']="monospace";
		var elem_font=document.getElementById("area_font_size");	
		if(elem_font){	
			for(var i=0; i<elem_font.length; i++){
				if(elem_font.options[i].value && elem_font.options[i].value == this.settings["font_size"])
						elem_font.options[i].selected=true;
			}
		}
		
		// calc line height
		document.getElementById("test_font_size").style.fontFamily= ""+this.settings["font_family"];
		document.getElementById("test_font_size").style.fontSize= this.settings["font_size"]+"pt";				
		document.getElementById("test_font_size").innerHTML="0";		
		this.lineHeight= document.getElementById("test_font_size").offsetHeight;

		
		for(var i=0; i<elems.length; i++){
			var elem= document.getElementById(elems[i]);	
			document.getElementById(elems[i]).style.fontFamily= this.settings["font_family"];
			document.getElementById(elems[i]).style.fontSize= this.settings["font_size"]+"pt";
			document.getElementById(elems[i]).style.lineHeight= this.lineHeight+"px";

		}
		if(this.nav['isOpera']){	// opera doesn't update font change to the textarea
			var start=this.textarea.selectionStart;
			var end= this.textarea.selectionEnd;
			var parNod = this.textarea.parentNode, nxtSib = this.textarea.nextSibling;
			parNod.removeChild(this.textarea); parNod.insertBefore(this.textarea, nxtSib);
			this.area_select(start, end-start);
		}
		
		this.add_style("pre{font-family:"+this.settings["font_family"]+"}");
		
		//alert(	getAttribute(document.getElementById("edit_area_test_font_size"), "style"));
		

		//alert("font "+this.textarea.style.font);
		// force update of selection field
		this.last_line_selected=-1;
		//if(this.state=="loaded"){
		this.last_selection= new Array();
		this.resync_highlight();
		//}
	/*	this.last_selection["indexOfCursor"]=-1;
		this.last_selection["curr_pos"]=-1;
		this.last_selection["line_start"]=-1;
		this.focus();*/
		//this.check_line_selection(false);
		//alert("line_h"+ this.lineHeight + " this.id: "+this.id+ "(size: "+size+")");
	};
	
	EditArea.prototype.change_font_size= function(){
		var size=document.getElementById("area_font_size").value;
		if(size>0)
			this.set_font("", size);			
	};
	
	
	EditArea.prototype.open_inline_popup= function(popup_id){
		this.close_all_inline_popup();
		var popup= document.getElementById(popup_id);		
		var editor= document.getElementById("editor");
		
		// search matching icon
		for(var i=0; i<this.inlinePopup.length; i++){
			if(this.inlinePopup[i]["popup_id"]==popup_id){
				var icon= document.getElementById(this.inlinePopup[i]["icon_id"]);
				if(icon){
					this.switchClassSticky(icon, 'editAreaButtonSelected', true);			
					break;
				}
			}
		}
		// check size
		popup.style.height="auto";
		popup.style.overflow= "visible";
			
		if(document.body.offsetHeight< popup.offsetHeight){
			popup.style.height= (document.body.offsetHeight-10)+"px";
			popup.style.overflow= "auto";
		}
		
		if(!popup.positionned){
			var new_left= editor.offsetWidth /2 - popup.offsetWidth /2;
			var new_top= editor.offsetHeight /2 - popup.offsetHeight /2;
			//var new_top= area.offsetHeight /2 - popup.offsetHeight /2;
			//var new_left= area.offsetWidth /2 - popup.offsetWidth /2;
			//alert("new_top: ("+new_top+") = calculeOffsetTop(area) ("+calculeOffsetTop(area)+") + area.offsetHeight /2("+ area.offsetHeight /2+") - popup.offsetHeight /2("+popup.offsetHeight /2+") - scrollTop: "+document.body.scrollTop);
			popup.style.left= new_left+"px";
			popup.style.top= new_top+"px";
			popup.positionned=true;
		}
		popup.style.visibility="visible";
		
		//popup.style.display="block";
	};

	EditArea.prototype.close_inline_popup= function(popup_id){
		var popup= document.getElementById(popup_id);		
		// search matching icon
		for(var i=0; i<this.inlinePopup.length; i++){
			if(this.inlinePopup[i]["popup_id"]==popup_id){
				var icon= document.getElementById(this.inlinePopup[i]["icon_id"]);
				if(icon){
					this.switchClassSticky(icon, 'editAreaButtonNormal', false);			
					break;
				}
			}
		}
		
		popup.style.visibility="hidden";	
	};
	
	EditArea.prototype.close_all_inline_popup= function(e){
		for(var i=0; i<this.inlinePopup.length; i++){
			this.close_inline_popup(this.inlinePopup[i]["popup_id"]);		
		}
		this.textarea.focus();
	};
	
	EditArea.prototype.show_help= function(){
		
		this.open_inline_popup("edit_area_help");
		
	};
			
	EditArea.prototype.new_document= function(){
		this.textarea.value="";
		this.area_select(0,0);
	};
	
	EditArea.prototype.get_all_toolbar_height= function(){
		var area= document.getElementById("editor");
		var results= parent.getChildren(area, "div", "class", "area_toolbar", "all", "0");	// search only direct children
		//results= results.concat(getChildren(area, "table", "class", "area_toolbar", "all", "0"));
		var height=0;
		for(var i=0; i<results.length; i++){			
			height+= results[i].offsetHeight;
		}
		//alert("toolbar height: "+height);
		return height;
	};
	
	EditArea.prototype.go_to_line= function(line){	
		if(!line)
		{	
			var icon= document.getElementById("go_to_line");
			if(icon != null){
				this.restoreClass(icon);
				this.switchClassSticky(icon, 'editAreaButtonSelected', true);
			}
			
			line= prompt(this.get_translation("go_to_line_prompt"));
			if(icon != null)
				this.switchClassSticky(icon, 'editAreaButtonNormal', false);
		}
		if(line && line!=null && line.search(/^[0-9]+$/)!=-1){
			var start=0;
			var lines= this.textarea.value.split("\n");
			if(line > lines.length)
				start= this.textarea.value.length;
			else{
				for(var i=0; i<Math.min(line-1, lines.length); i++)
					start+= lines[i].length + 1;
			}
			this.area_select(start, 0);
		}
		
		
	};
	
	
	EditArea.prototype.change_smooth_selection_mode= function(setTo){
		//alert("setTo: "+setTo);
		if(this.do_highlight)
			return;
			
		if(setTo != null){
			if(setTo === false)
				this.smooth_selection=true;
			else
				this.smooth_selection=false;
		}
		var icon= document.getElementById("change_smooth_selection");
		this.textarea.focus();
		if(this.smooth_selection===true){
			//setAttribute(icon, "class", getAttribute(icon, "class").replace(/ selected/g, "") );
			/*setAttribute(icon, "oldClassName", "editAreaButtonNormal" );
			setAttribute(icon, "className", "editAreaButtonNormal" );*/
			//this.restoreClass(icon);
			//this.restoreAndSwitchClass(icon,'editAreaButtonNormal');
			this.switchClassSticky(icon, 'editAreaButtonNormal', false);
			
			this.smooth_selection=false;
			document.getElementById("selection_field").style.display= "none";
			document.getElementById("cursor_pos").style.display= "none";
			document.getElementById("end_bracket").style.display= "none";
		}else{
			//setAttribute(icon, "class", getAttribute(icon, "class") + " selected");
			//this.switchClass(icon,'editAreaButtonSelected');
			this.switchClassSticky(icon, 'editAreaButtonSelected', false);
			this.smooth_selection=true;
			document.getElementById("selection_field").style.display= "block";
			document.getElementById("cursor_pos").style.display= "block";
			document.getElementById("end_bracket").style.display= "block";
		}	
	};
	
	// the auto scroll of the textarea has some lacks when it have to show cursor in the visible area when the textarea size change
	// show spécifiy whereas it is the "top" or "bottom" of the selection that is showned
	EditArea.prototype.scroll_to_view= function(show){
		if(!this.smooth_selection)
			return;
		var zone= document.getElementById("result");
		
		//var cursor_pos_top= parseInt(document.getElementById("cursor_pos").style.top.replace("px",""));
		var cursor_pos_top= document.getElementById("cursor_pos").cursor_top;
		if(show=="bottom")
			cursor_pos_top+= (this.last_selection["line_nb"]-1)* this.lineHeight;
			
		var max_height_visible= zone.clientHeight + zone.scrollTop;
		var miss_top= cursor_pos_top + this.lineHeight - max_height_visible;
		if(miss_top>0){
			//alert(miss_top);
			zone.scrollTop=  zone.scrollTop + miss_top;
		}else if( zone.scrollTop > cursor_pos_top){
			// when erase all the content -> does'nt scroll back to the top
			//alert("else: "+cursor_pos_top);
			zone.scrollTop= cursor_pos_top;	 
		}
		//var cursor_pos_left= parseInt(document.getElementById("cursor_pos").style.left.replace("px",""));
		var cursor_pos_left= document.getElementById("cursor_pos").cursor_left;
		var max_width_visible= zone.clientWidth + zone.scrollLeft;
		var miss_left= cursor_pos_left + 10 - max_width_visible;
		if(miss_left>0){			
			zone.scrollLeft= zone.scrollLeft + miss_left+ 50;
		}else if( zone.scrollLeft > cursor_pos_left){
			zone.scrollLeft= cursor_pos_left ;
		}else if( zone.scrollLeft == 45){
			// show the line numbers if textarea align to it's left
			zone.scrollLeft=0;
		}
		/*if(miss_top> 0 || miss_left >0)
			alert("miss top: "+miss_top+" miss left: "+miss_left);*/
	};
	
	EditArea.prototype.check_undo= function(){
		if(!editAreas[this.id])
			return false;
		if(this.textareaFocused && editAreas[this.id]["displayed"]==true){
			var text=this.textarea.value;
			if(this.previous.length<=1)
				this.switchClassSticky(document.getElementById("undo"), 'editAreaButtonDisabled', true);
			/*var last= 0;
			for( var i in this.previous){
				last=i;
			}*/
			if(!this.previous[this.previous.length-1] || this.previous[this.previous.length-1]["text"] != text){
				this.previous.push({"text": text, "selStart": this.textarea.selectionStart, "selEnd": this.textarea.selectionEnd});
				if(this.previous.length > this.settings["max_undo"]+1)
					this.previous.shift();
				
			}
			if(this.previous.length == 2)
				this.switchClassSticky(document.getElementById("undo"), 'editAreaButtonNormal', false);
		}
			//if(this.previous[0] == text)	
		setTimeout("editArea.check_undo()", 3000);
	};
	
	EditArea.prototype.undo= function(){
		//alert("undo"+this.previous.length);
		if(this.previous.length > 0){
			if(this.nav['isIE'])
				this.getIESelection();
		//	var pos_cursor=this.textarea.selectionStart;
			this.next.push({"text": this.textarea.value, "selStart": this.textarea.selectionStart, "selEnd": this.textarea.selectionEnd});
			var prev= this.previous.pop();
			if(prev["text"]==this.textarea.value && this.previous.length > 0)
				prev=this.previous.pop();						
			this.textarea.value= prev["text"];
			this.last_undo= prev["text"];
			this.area_select(prev["selStart"], prev["selEnd"]-prev["selStart"]);
			this.switchClassSticky(document.getElementById("redo"), 'editAreaButtonNormal', false);
			this.resync_highlight(true);
			//alert("undo"+this.previous.length);
		}
	};
	
	EditArea.prototype.redo= function(){
		if(this.next.length > 0){
			/*if(this.nav['isIE'])
				this.getIESelection();*/
			//var pos_cursor=this.textarea.selectionStart;
			var next= this.next.pop();
			this.previous.push(next);
			this.textarea.value= next["text"];
			this.last_undo= next["text"];
			this.area_select(next["selStart"], next["selEnd"]-next["selStart"]);
			this.switchClassSticky(document.getElementById("undo"), 'editAreaButtonNormal', false);
			this.resync_highlight(true);
		}
		if(	this.next.length == 0)
			this.switchClassSticky(document.getElementById("redo"), 'editAreaButtonDisabled', true);
	};
	
	EditArea.prototype.check_redo= function(){
		if(editArea.next.length > 0 && editArea.textarea.value!=editArea.last_undo){
			editArea.next= new Array();	// undo the ability to use "redo" button
			editArea.switchClassSticky(document.getElementById("redo"), 'editAreaButtonDisabled', true);
		}
	};
	
	
	// functions that manage icons roll over, disabled, etc...
	EditArea.prototype.switchClass = function(element, class_name, lock_state) {
		var lockChanged = false;
	
		if (typeof(lock_state) != "undefined" && element != null) {
			element.classLock = lock_state;
			lockChanged = true;
		}
	
		if (element != null && (lockChanged || !element.classLock)) {
			element.oldClassName = element.className;
			element.className = class_name;
		}
	};
	
	EditArea.prototype.restoreAndSwitchClass = function(element, class_name) {
		if (element != null && !element.classLock) {
			this.restoreClass(element);
			this.switchClass(element, class_name);
		}
	};
	
	EditArea.prototype.restoreClass = function(element) {
		if (element != null && element.oldClassName && !element.classLock) {
			element.className = element.oldClassName;
			element.oldClassName = null;
		}
	};
	
	EditArea.prototype.setClassLock = function(element, lock_state) {
		if (element != null)
			element.classLock = lock_state;
	};
	
	EditArea.prototype.switchClassSticky = function(element, class_name, lock_state) {
		var lockChanged = false;
		if (typeof(lock_state) != "undefined" && element != null) {
			element.classLock = lock_state;
			lockChanged = true;
		}
	
		if (element != null && (lockChanged || !element.classLock)) {
			element.className = class_name;
			element.oldClassName = class_name;
	
			// Fix opacity in Opera
			if (this.nav['isOpera']) {
				if (class_name == "mceButtonDisabled") {
					var suffix = "";
	
					if (!element.mceOldSrc)
						element.mceOldSrc = element.src;
	
					if (this.operaOpacityCounter > -1)
						suffix = '?rnd=' + this.operaOpacityCounter++;
	
					element.src = this.baseURL + "/images/opacity.png" ;
					element.style.backgroundImage = "url('" + element.mceOldSrc + "')";
				} else {
					if (element.mceOldSrc) {
						element.src = element.mceOldSrc;
						element.parentNode.style.backgroundImage = "";
						element.mceOldSrc = null;
					}
				}
			}
		}
	};
	
	//make the "page up" and "page down" buttons works correctly
	EditArea.prototype.scroll_page= function(params){
		var dir= params["dir"];
		var shift_pressed= params["shift"];
		screen_height=document.getElementById("result").clientHeight;
		var lines= this.textarea.value.split("\n");		
		var new_pos=0;
		var length=0;
		var char_left=0;
		var line_nb=0;
		if(dir=="up"){
			//val= Math.max(0, document.getElementById("result").scrollTop - screen_height);
			//document.getElementById("result").scrollTop= val;
			var scroll_line= Math.ceil((screen_height -30)/this.lineHeight);
			if(this.last_selection["selec_direction"]=="up"){
				for(line_nb=0; line_nb< Math.min(this.last_selection["line_start"]-scroll_line, lines.length); line_nb++){
					new_pos+= lines[line_nb].length + 1;
				}
				char_left=Math.min(lines[Math.min(lines.length-1, line_nb)].length, this.last_selection["curr_pos"]-1);
				if(shift_pressed)
					length=this.last_selection["selectionEnd"]-new_pos-char_left;	
				this.area_select(new_pos+char_left, length);
				view="top";
			}else{			
				view="bottom";
				for(line_nb=0; line_nb< Math.min(this.last_selection["line_start"]+this.last_selection["line_nb"]-1-scroll_line, lines.length); line_nb++){
					new_pos+= lines[line_nb].length + 1;
				}
				char_left=Math.min(lines[Math.min(lines.length-1, line_nb)].length, this.last_selection["curr_pos"]-1);
				if(shift_pressed){
					//length=this.last_selection["selectionEnd"]-new_pos-char_left;	
					start= Math.min(this.last_selection["selectionStart"], new_pos+char_left);
					length= Math.max(new_pos+char_left, this.last_selection["selectionStart"] )- start ;
					if(new_pos+char_left < this.last_selection["selectionStart"])
						view="top";
				}else
					start=new_pos+char_left;
				this.area_select(start, length);
				
			}
		}else{
			//val= Math.max(document.getElementById("result").style.height.replace("px", ""), document.getElementById("result").scrollTop + screen_height);
			//document.getElementById("result").scrollTop= val;
			var scroll_line= Math.floor((screen_height-30)/this.lineHeight);				
			if(this.last_selection["selec_direction"]=="down"){
				view="bottom";
				for(line_nb=0; line_nb< Math.min(this.last_selection["line_start"]+this.last_selection["line_nb"]-2+scroll_line, lines.length); line_nb++){
					if(line_nb==this.last_selection["line_start"]-1)
						char_left= this.last_selection["selectionStart"] -new_pos;
					new_pos+= lines[line_nb].length + 1;
									
				}
				if(shift_pressed){
					length=Math.abs(this.last_selection["selectionStart"]-new_pos);	
					length+=Math.min(lines[Math.min(lines.length-1, line_nb)].length, this.last_selection["curr_pos"]);
					//length+=Math.min(lines[Math.min(lines.length-1, line_nb)].length, char_left);
					this.area_select(Math.min(this.last_selection["selectionStart"], new_pos), length);
				}else{
					this.area_select(new_pos+char_left, 0);
				}
				
			}else{
				view="top";
				for(line_nb=0; line_nb< Math.min(this.last_selection["line_start"]+scroll_line-1, lines.length, lines.length); line_nb++){
					if(line_nb==this.last_selection["line_start"]-1)
						char_left= this.last_selection["selectionStart"] -new_pos;
					new_pos+= lines[line_nb].length + 1;									
				}
				if(shift_pressed){
					length=Math.abs(this.last_selection["selectionEnd"]-new_pos-char_left);	
					length+=Math.min(lines[Math.min(lines.length-1, line_nb)].length, this.last_selection["curr_pos"])- char_left-1;
					//length+=Math.min(lines[Math.min(lines.length-1, line_nb)].length, char_left);
					this.area_select(Math.min(this.last_selection["selectionEnd"], new_pos+char_left), length);
					if(new_pos+char_left > this.last_selection["selectionEnd"])
						view="bottom";
				}else{
					this.area_select(new_pos+char_left, 0);
				}
				
			}
		}		
		
		this.check_line_selection();
		this.scroll_to_view(view);
	};
	
	EditArea.prototype.start_resize= function(e){		
		parent.editAreaLoader.resize["id"]= editArea.id;		
		parent.editAreaLoader.resize["start_x"]= (e)? e.pageX : event.x + document.body.scrollLeft;		
		parent.editAreaLoader.resize["start_y"]= (e)? e.pageY : event.y + document.body.scrollTop;
		if(editArea.nav['isIE']){
			editArea.textarea.focus();
			editArea.getIESelection();
		}
		parent.editAreaLoader.resize["selectionStart"]= editArea.textarea.selectionStart;
		parent.editAreaLoader.resize["selectionEnd"]= editArea.textarea.selectionEnd;
		/*parent.editAreaLoader.resize["frame_top"]= parent.calculeOffsetTop(parent.editAreas[editArea.id]["textarea"]);
		/*parent.editAreaLoader.resize["frame_left"]= parent.calculeOffsetLeft(parent.frames[editArea.id]);*/
		parent.editAreaLoader.start_resize_area();
	};
	
	EditArea.prototype.toggle_full_screen= function(to){
		if(typeof(to)=="undefined")
			to= !this.fullscreen['isFull'];
		var old= this.fullscreen['isFull'];
		this.fullscreen['isFull']= to;
		var icon= document.getElementById("fullscreen");
		if(to && to!=old)
		{	// toogle on fullscreen		
			var selStart= this.textarea.selectionStart;
			var selEnd= this.textarea.selectionEnd;
			var html= parent.document.getElementsByTagName("html")[0];
			var frame= parent.document.getElementById("frame_"+this.id);

			this.fullscreen['old_overflow']= parent.get_css_property(html, "overflow");
			this.fullscreen['old_height']= parent.get_css_property(html, "height");
			this.fullscreen['old_width']= parent.get_css_property(html, "width");
			this.fullscreen['old_scrollTop']= html.scrollTop;
			this.fullscreen['old_scrollLeft']= html.scrollLeft;
			this.fullscreen['old_zIndex']= parent.get_css_property(frame, "z-index");
			if(this.nav['isOpera']){
				html.style.height= "100%";
				html.style.width= "100%";	
			}
			html.style.overflow= "hidden";
			html.scrollTop=0;
			html.scrollLeft=0;
			
		
			//html.style.backgroundColor= "#FF0000"; 
//	alert(screen.height+"\n"+window.innerHeight+"\n"+html.clientHeight+"\n"+window.offsetHeight+"\n"+document.body.offsetHeight);
			
			
			frame.style.position="absolute";
			frame.style.width= html.clientWidth+"px";
			frame.style.height= html.clientHeight+"px";
			frame.style.display="block";
			frame.style.zIndex="999999";
			frame.style.top="0px";
			frame.style.left="0px";
			
			// if the iframe was in a div with position absolute, the top and left are the one of the div, 
			// so I fix it by seeing at witch position the iframe start and correcting it
			frame.style.top= "-"+parent.calculeOffsetTop(frame)+"px";
			frame.style.left= "-"+parent.calculeOffsetLeft(frame)+"px";
			
		//	parent.editAreaLoader.execCommand(this.id, "update_size();");
		//	var body=parent.document.getElementsByTagName("body")[0];
		//	body.appendChild(frame);
			
			this.switchClassSticky(icon, 'editAreaButtonSelected', false);
			this.fullscreen['allow_resize']= this.resize_allowed;
			this.allow_resize(false);
	
			//this.area_select(selStart, selEnd-selStart);
			
		
			// opera can't manage to do a direct size update
			if(this.nav['isFirefox']){
				parent.editAreaLoader.execCommand(this.id, "update_size();");
				this.area_select(selStart, selEnd-selStart);
				this.scroll_to_view();
				this.focus();
			}else{
				setTimeout("parent.editAreaLoader.execCommand('"+ this.id +"', 'update_size();');editArea.focus();", 10);
			}	
			
	
		}
		else if(to!=old)
		{	// toogle off fullscreen
			var selStart= this.textarea.selectionStart;
			var selEnd= this.textarea.selectionEnd;
			
			var frame= parent.document.getElementById("frame_"+this.id);	
			frame.style.position="static";
			frame.style.zIndex= this.fullscreen['old_zIndex'];
		
			var html= parent.document.getElementsByTagName("html")[0];
		//	html.style.overflow= this.fullscreen['old_overflow'];
		
			if(this.nav['isOpera']){
				html.style.height= "auto"; 
				html.style.width= "auto";
				html.style.overflow= "auto";
			}else if(this.nav['isIE'] && parent!=top){	// IE doesn't manage html overflow in frames like in normal page... 
				html.style.overflow= "auto";
			}
			else
				html.style.overflow= this.fullscreen['old_overflow'];
			html.scrollTop= this.fullscreen['old_scrollTop'];
			html.scrollTop= this.fullscreen['old_scrollLeft'];
		
			parent.editAreaLoader.hide(this.id);
			parent.editAreaLoader.show(this.id);
			
			this.switchClassSticky(icon, 'editAreaButtonNormal', false);
			if(this.fullscreen['allow_resize'])
				this.allow_resize(this.fullscreen['allow_resize']);
			if(this.nav['isFirefox']){
				this.area_select(selStart, selEnd-selStart);
				setTimeout("editArea.scroll_to_view();", 10);
			}			
			
			//parent.editAreaLoader.remove_event(parent.window, "resize", editArea.update_size);
		}
		
	};
	
	EditArea.prototype.allow_resize= function(allow){
		var resize= document.getElementById("resize_area");
		if(allow){
			
			resize.style.visibility="visible";
			parent.editAreaLoader.add_event(resize, "mouseup", editArea.start_resize);
		}else{
			resize.style.visibility="hidden";
			parent.editAreaLoader.remove_event(resize, "mouseup", editArea.start_resize);
		}
		this.resize_allowed= allow;
	};


