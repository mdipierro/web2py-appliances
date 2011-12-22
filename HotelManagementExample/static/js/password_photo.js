jQuery(document).ready(function(){
    jQuery('#photo_password__row').hide();
    jQuery('#photo_visibility').change(function(){
        if (jQuery('#photo_visibility option[value = Protected]').attr('selected'))
            jQuery('#photo_password__row').show();
        else 
            jQuery('#photo_password__row').hide();});
});
