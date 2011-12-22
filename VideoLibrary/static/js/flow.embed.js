/**
 * flowembed 0.11. Flowplayer embedding script
 * 
 * http://flowplayer.org/tools/flow-embed.html
 *
 * Copyright (c) 2008 Tero Piirainen (tero@flowplayer.org)
 *
 * Released under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 * 
 * >> Basically you can do anything you want but leave this header as is <<
 *
 * Version: 0.10 - 05/19/2008
 */ 
(function($) {		
	
	// jQuery plugin initialization
	$.fn.extend({
		flowembed: function(params, config, opts) { 			
			return this.each(function() {
				new flowembed($(this), params, config, opts);
			});
		}
	});
					
			
	function flowembed(root, params, config, embedOpts) {
	
		var opts = {
			oneInstance: true,
			activeClass: 'playing',
			overlayClass: 'playButton',
			fallback: null
		};	
		
		$.extend(opts, embedOpts);
		var player = null;
		config = config || {};
		if (typeof params == 'string') params = {src:params};
		
		root.click(function(event) {			
			
			// disable default behaviour
			event.preventDefault();
			
			if (root.find("embed, object").length) return false;
				
			// if oneInstance = true, resume previously playing video	
			if (opts.oneInstance) onClipDone();
			
			// save nested HTML content for resuming purposes
			root.addClass(opts.activeClass).data("html", root.html());
			
			// build flowplayer with videoFile supplied in href- attribute
			var href = root.attr("href");
			config.videoFile = href; 			

			// possible fallback
			if (opts.fallback && !flashembed.isSupported([9,115])) {
				config.videoFile = href.substring(0, href.lastIndexOf(".") + 1) + opts.fallback;				
			}			
			
			player = flashembed(this, params, {config:config});
			
		}); 

		// create play button on top of splash image
		root.append($("<div/>").addClass(opts.overlayClass));

		
		/* 
			this function is called by Flowplayer when playback finishes. 
			it makes currently playing video to oneInstance it's original
			HTML stage.
		*/
		if (opts.oneInstance && !$.isFunction("onClipDone")) {			
			window.onClipDone = function() {
				$("." + opts.activeClass).each(function() {
					$(this).html($(this).data("html")).removeClass(opts.activeClass);	
				});
			};			
		} 
	}

})(jQuery);
