from gluon import current
T = current.T

def sizeof_file(num):
        for x in [T('bytes'),T('KB'),T('MB'),T('GB')]:
            if num < 1024.0 and num > -1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, T('TB'))

def strip_accents(s):
   import unicodedata
   return ''.join(c for c in unicodedata.normalize('NFD', s.decode('utf-8'))
                  if unicodedata.category(c) != 'Mn')