def translate():
    return "jQuery(document).ready(function(){jQuery('p,ul,div,a').translate('%s');});" % request.args(0).split('.')[0]

