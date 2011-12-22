import os
import re

files_dir = {}
files_dir.update({'./views/': '.html'})
files_dir.update({'./views/default/': '.html'})
files_dir.update({'./views/pm/': '.html'})
files_dir.update({'./views/zadmin/': '.html'})
files_dir.update({'./controllers/': '.py'})

text_list = []
processed_files = []
for each_dir, ext in files_dir.items():
    for file in os.listdir(each_dir):
        fname = os.path.join(each_dir, file)
        if os.path.isfile(fname) and os.path.splitext(fname)[-1] == ext:
            processed_files.append(fname)
            han = open(fname, "r")
            data = han.read()
            output  = re.compile(r'({{\=XML\(T\(\')(.*?)(\'\)\)}})', re.DOTALL | re.IGNORECASE).findall(data)
            han.close()
            for text in output:
                if not text[1] in text_list:
                    text_list.append(text[1])

text_list.sort()
#print '\n'.join(text_list)
print '{'
for text in text_list:
    print "'%s': ''," % (text)
print '}'
#print '\n'.join(processed_files)