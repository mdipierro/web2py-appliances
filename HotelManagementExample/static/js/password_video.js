jQuery(document).ready(function(){
    jQuery('#video_password__row').hide();
    jQuery('#video_visibility').change(function(){
        if (jQuery('#video_visibility option[value = Protected]').attr('selected'))
            jQuery('#video_password__row').show();
        else 
            jQuery('#video_password__row').hide();});
});
