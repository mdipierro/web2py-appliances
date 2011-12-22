# Provides a secure html/xhtml parser for the system
# Use from your controllers:
# text = parse_content(text)

import sgmllib, string
from gluon.html import URL
import re

class StrippingParser(sgmllib.SGMLParser):
    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'i', 'u', 'code',)
    tolerate_missing_closing_tags = ('br',)
    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__(self, mode):
        sgmllib.SGMLParser.__init__(self)
        self.result = []
        self.endTagList = []
        self.mode = mode

    def handle_data(self, data):
        self.result.append(data)

    def handle_charref(self, name):
        self.result.append("&#%s;" % name)

    def handle_entityref(self, name):
        x = ';' * self.entitydefs.has_key(name)
        self.result.append("&%s%s" % (name, x))

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones. """
        if self.mode == "removeall":
            if tag in self.valid_tags:
                self.result.append('<' + tag)
                for k, v in attrs:
                    if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                        self.result.append(' %s="%s"' % (k, v))
                self.result.append('>')
                if tag not in self.tolerate_missing_closing_tags:
                    endTag = '</%s>' % tag
                    self.endTagList.insert(0,endTag)

    def unknown_endtag(self, tag):
        if self.mode == "removeall":
            if tag in self.valid_tags:
                # We don't ensure proper nesting of opening/closing tags
                endTag = '</%s>' % tag
                self.result.append(endTag)
                self.endTagList.remove(endTag)

    def cleanup(self):
        """ Append missing closing tags. """
        self.result.extend(self.endTagList)

    def get_html(self):
        html = ' '.join(self.result)
        #html = html.replace('<br>', '<br />')
        #html = html.replace('\r\n', '\n') # Windows
        #html = html.replace('\n', '<br />')
        return html

    def parse_emoticons(self, html_code):
        """ This is pyForum Specific """
        # Emoticon Handling
        emoticons = ['icon_arrow.png', 'icon_biggrin.png', 'icon_confused.png', 'icon_cool.png', 'icon_cry.png', 'icon_exclaim.png', 'icon_idea.png', 'icon_lol.png', 'icon_mad.png', 'icon_mrgreen.png', 'icon_neutral.png', 'icon_question.png', 'icon_razz.png', 'icon_redface.png', 'icon_rolleyes.png', 'icon_sad.png', 'icon_smile.png', 'icon_twisted.png', 'icon_wink.png']
        for icon in emoticons:
            replace_tag = (icon[5:icon.rfind('.')])
            replace_tag_with = '<img src="%s" alt="%s" style="width:16px;height:16px;" class="imgclear" style="vertical-align:middle;" />' % (URL(r=request, c='static/images', f=icon), replace_tag)
            html_code = html_code.replace(':%s:' % (replace_tag), replace_tag_with)
        return html_code
        
    def parse_pseudo_html(self, html_code):
        """ This is also pyForum Specific """
        tags = {'[b]': '<b>',
                '[/b]': '</b>',
                '[u]': '<u>',
                '[/u]': '</u>',
                '[i]': '<i>',
                '[/i]': '</i>',
                '[code]': '<pre class="code">',
                '[/code]': '</pre>',
                '[quote]': '<div class="quote"><div>',
                '[/quote]': '</div></div>',
                '[small]': '<span class="small">',
                '[/small]': '</span>',
                '[smallb]': '<span class="smallb">',
                '[/smallb]': '</span>'}
        pseudo_html = self.multiple_replace(tags, html_code)
        # Now on to URLs
        pseudo_html = re.sub('(\[url\])(.*?)(\[/url\])', '<a href="\\2" title="\\2">\\2</a>', pseudo_html)
        # Next images
        pseudo_html = re.sub('(\[img\])(.*?)(\[/img\])', '<img src="\\2" alt="\\2" />', pseudo_html)
        
        # !NEW CODE
        #     Added code to parse media tags and convert them into code to embed those links in the page
        # Video files - YouTube
        pseudo_html = re.sub('(\[youtube\])(.*?)(\[/youtube\])', '<iframe title="YouTube video player" width="480" height="390" src="\\2" frameborder="0" allowfullscreen></iframe>', pseudo_html)
        # Video files - Vimeo
        pseudo_html = re.sub('(\[vimeo\])(.*?)(\[/vimeo\])', '<iframe title="Vimeo video player" width="480" height="390" src="\\2" frameborder="0" allowfullscreen></iframe>', pseudo_html)
        # Music files
        pseudo_html = re.sub('(\[music\])(.*?)(\[/music\])', '<embed src="\\2" width="256" height="60" controls="console" autostart="false" loop="false"></embed>', pseudo_html)
        # !END NEW CODE
        
        # and finally some formatting for the final display
        pseudo_html = pseudo_html.replace('<br>', '<br />')
        pseudo_html = pseudo_html.replace('\r\n', '<br />') # Windows
        pseudo_html = pseudo_html.replace('\n', '<br />')
        return pseudo_html
        
    def multiple_replace(self, dict, html_code): 
        """ Replace in 'text' all occurences of any key in the given
        dictionary by its corresponding value.  Returns the new tring.""" 
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], html_code) 


def parse_content(content, mode="removeall"):
    """ Parse the messages mode can be "removeall", "forumpreview" and "forumfull" """
    if content.strip():
        parser = StrippingParser(mode)
        new_content = content
        if mode == "forumpreview":
            # Here we need to "trick" the parser and "pre-convert" our custom-html
            # code from :pseudocode: into the "real" html, so it is stripped off
            new_content = parser.parse_emoticons(new_content)
            new_content = parser.parse_pseudo_html(new_content)
            
        parser.feed(new_content)
        parser.close()
        parser.cleanup()
        clean_content = parser.get_html()
        if mode == "forumfull":
            # Here we need to "convert" emoticons and images
            clean_content = parser.parse_emoticons(clean_content)
            clean_content = parser.parse_pseudo_html(clean_content)
    else:
        clean_content = ''
    return clean_content
