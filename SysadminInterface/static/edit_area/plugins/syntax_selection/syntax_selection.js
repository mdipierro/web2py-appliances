/**
 * Syntax selection plugin
 * by Christophe Dolivet (based on a plugin from Martin d'Allens)
 * v0.1 (2007/01/20)
 * 
 *    
 * This plugin allow the user to change the syntax definition in use. It adds a select in the toolbar.
 * 
 * - plugin name to add to the plugin list: "syntax_selection"
 * - plugin name to add to the toolbar list: "syntax_selection" 
 * - possible parameters to add to EditAreaLoader.init(): 
 * 		"syntax_selection_allow": (String) define a list separated by "," of possible language syntax to use (eg: "php,js,python,html") 
 *		 							(default: empty)
 * 
 * 
 */
    
var EditArea_syntax_selection= {
	/**
	 * Get called once this file is loaded (editArea still not initialized)
	 *
	 * @return nothing	 
	 */	 	 	
	init: function(){	
		this.syntax_list= new Array();
		this.allready_used_syntax= new Object();
		
		// retrieve the init parameter
		if(editArea.settings["syntax_selection_allow"] && editArea.settings["syntax_selection_allow"].length>0)
			this.syntax_list= editArea.settings["syntax_selection_allow"].replace(/ /g,"").split(",");
		
		if(editArea.settings['syntax'])
			this.allready_used_syntax[editArea.settings['syntax']]=true;

	}
	/**
	 * Returns the HTML code for a specific control.
	 * 
	 * @param {string} ctrl_name: the name of the control to add	  
	 * @return HTML code for a specific control or false.
	 * @type string	or boolean
	 */	
	,get_control_html: function(ctrl_name){
		switch(ctrl_name){
			case "syntax_selection":
				var html= "<select id='syntax_selection' onchange='javascript:editArea.execCommand(\"syntax_selection_change\")'>";
				html+="<option value='-1'>{$syntax_selection}</option>";
				for(var i=0; i<this.syntax_list.length; i++) {
					var syntax= this.syntax_list[i];
					
					html+= "<option value='" + syntax + "'";
					if(editArea.settings['syntax'] == syntax)
						html+= " selected=\"selected\" ";
					
					html+= ">{$syntax_" + syntax + "}</option>";
				}
				
				html+= "</select>";
				return html;
		}
		return false;
	}
	/**
	 * Get called once EditArea is fully loaded and initialised
	 *	 
	 * @return nothing
	 */	 	 	
	,onload: function(){ 
		// load need languages
		for(var i=0; i<this.syntax_list.length; i++)
			parent.editAreaLoader.load_script(parent.editAreaLoader.baseURL + "reg_syntax/" + this.syntax_list[i] + ".js");
			
		
	}
	
	/**
	 * Is called each time the user presses a keyboard key.
	 *	 
	 * @param (event) e: the keydown event
	 * @return true - pass to next handler in chain, false - stop chain execution
	 * @type boolean
	 */
	,onkeydown: function(e){
		return true;
	}
	
	/**
	 * Executes a specific command, this function handles plugin commands.
	 *
	 * @param {string} cmd: the name of the command being executed
	 * @param {unknown} param: the parameter of the command	 
	 * @return true - pass to next handler in chain, false - stop chain execution
	 * @type boolean	
	 */
	,execCommand: function(cmd, param){
		// Handle commands
		switch(cmd) {
			case "syntax_selection_change":
				var new_syntax= document.getElementById("syntax_selection").value;
				if(new_syntax!=-1)
				{
					if(!this.allready_used_syntax[new_syntax])
					{	// the syntax has still not been used
						// rebuild syntax definition for new languages
						parent.editAreaLoader.init_syntax_regexp();
						// add style to the new list
						editArea.add_style(parent.editAreaLoader.syntax[new_syntax]["styles"]);
						this.allready_used_syntax[new_syntax]=true;
					}
					editArea.settings['syntax']= new_syntax;
					editArea.resync_highlight();
				}
				return false;
		}
		// Pass to next handler in chain
		return true;
	}
};

// Adds the plugin class to the list of available EditArea plugins
editArea.add_plugin("syntax_selection", EditArea_syntax_selection);
