import sys
import os
import re
import time
import hashlib
import itertools
import logging
import fnmatch
import datetime
import urllib



META_CATALOG = 'meta.catalog'
PATTERN_GROUP = '\d+(?=[^\d]*$)'
PATTERN_IGNORE = '(\..+)|(.+\~)'
regex_pattern = re.compile(PATTERN_GROUP)
regex_extension = re.compile('\.[a-zA-Z]{1,5}$')

logging.basicConfig(level=logging.INFO)

class Cataloger(object):

    regex = re.compile('.*/(?P<x>\d\d)(?P<t>\d+)f(?P<f>\d+)b(?P<b>\d+)(m(?P<m1>\d+))?(m(?P<m2>\d+))?(m(?P<m3>\d+))?.*/')

    @staticmethod
    def __volume(x,t):
        return 'volume/%s' % (x+'^3x'+t)

    @staticmethod
    def __flavor(f):
        if not f: return None
        return 'flavor/%s' % (f[0]+(f[1:] and '+'+f[1:] or ''))

    @staticmethod
    def __beta(b):
        if not b: return None
        return 'beta/%s' % float(b[0]+'.'+b[1:])

    @staticmethod
    def __mass(m):
        if not m: return None
        return 'mass/%s' % float('0.0'+m)

    @staticmethod
    def __tagmilc(folder):
        match = Cataloger.regex.match(folder)
        tags = []
        if match:
            for tag in [Cataloger.__volume(match.group('x'),match.group('t')),
                        Cataloger.__flavor(match.group('f')),
                        Cataloger.__beta(match.group('b')),
                        Cataloger.__mass(match.group('m1')),
                        Cataloger.__mass(match.group('m2'))]:
                if tag: tags.append(tag)
        tags.append('source/milc')
        return tags

    @staticmethod
    def __description(folder):
        if folder.count('/')<2: return ''
        if folder.count('/')==2: return 'Data from %s Collaboration' % folder.split('/')[1].upper()
        try:
            url ='http://qcd.nersc.gov/'+folder
            data = urllib.urlopen(url).read()
        except Exception, e:
            print e
            print '<<<<<<<<<<<<<<<<<<<<<'
            return "## This folder does not apper to be posted publicly"
        data = re.compile('<(a|A).*?href="(?P<link>.+?)".*?>(?P<content>.*?)</(a|A)>',re.DOTALL).sub('[[\g<content> \g<link>]]',data)
        data = re.compile("<(a|A).*?href='(?P<link>.+?)'.*?>(?P<content>.*?)</(a|A)>",re.DOTALL).sub('[[\g<content> \g<link>]]',data)
        data = re.compile('<(title|TITLE)>.*?</(title|TITLE)>',re.DOTALL).sub('',data)
        data = re.compile('</.*?>',re.DOTALL).sub(' ',data)
        # data = re.compile('<[hH]1.*?>\s*',re.DOTALL).sub('# ',data)
        # ignore titles
        data = re.compile('<[hH]1.*?>.*?\n',re.DOTALL).sub('',data)
        data = re.compile('<[hH]2.*?>\s*',re.DOTALL).sub('## ',data)
        data = re.compile('<[hH]3.*?>\s*',re.DOTALL).sub('### ',data)
        data = re.compile('<[hH]4.*?>\s*',re.DOTALL).sub('#### ',data)
        data = re.compile('[ ]*<(li|LI).*?>\s*',re.DOTALL).sub('\n\n',data) # should be - but html broken
        data = re.compile('\s*<(br|BR)[ ]*\?>\s*',re.DOTALL).sub('\n\n',data)
        data = re.compile('<(sup|SUP)[ ]*\?>',re.DOTALL).sub('^',data)
        data = re.compile('<.*?>',re.DOTALL).sub(' ',data)
        data = re.compile('\n\s+\n',re.DOTALL).sub('\n\n',data)
        data = re.compile('[ ]+',re.DOTALL).sub(' ',data)
        data = re.compile('\n[ ]+',re.DOTALL).sub('\n',data)
        data = data.replace('[[Ensemble directory dir.html]]','').strip()
        data = data.replace('&times;','x')
        data = data.replace('&lt;','<')
        data = data.replace('&gt;','>')
        data = data.replace('&amp;','&')
        data = data.replace('&beta;','beta')
        return data

    @staticmethod
    def build(folder):        
        if not folder.endswith('/'):
            folder=folder+'/'
        catalog={}
        catalog['title'] = folder
        if 'MILC' in folder: 
            catalog['tags'] = Cataloger.__tagmilc(folder)
        elif 'CU' in folder:
            catalog['tags'] = ['source/columbia_university']
        elif 'OSU' in folder:
            catalog['tags'] = ['source/oregon_state']
        elif 'BNL' in folder:
            catalog['tags'] = ['source/brokhaven_lab']
        catalog['header'] = Cataloger.__description(folder)
        return catalog


def parse_meta_catalog(filename):
    data = ('\n'+open(filename,'rb').read().replace('\r\n','\n')).split('\n==')
    d={}
    for section in data:
        if not section.strip(): continue
        name,body = section.split('\n',1)
        name,body=name.replace('=','').strip().lower(),body.strip()
        if name in ('ignore','search','group'):
            body = '|'.join('(%s)' % item for item in body.split('\n') if item.strip())
        if name in ('tags','access'):
            body = [tag.strip() for tag in body.split('\n') if tag.strip()]
        d[name]=body
        logging.info('found %s.%s' % (filename,name))
    return d

def folder_walker(path,n_ignore=0):
    """
    this file loops over all files in a directory structure recursively
    """
    for root, subpaths, filenames in os.walk(path):
        fullpath = os.path.join(path,root,filenames)
        size = os.path.getsize(fullpath)
        mtime = os.path.getmtime(fullpath) #### <<<< convert to datetime
        yield (fullpath[n:], size, mtime)

def ls_walker(filename,n_ignore=0):
    """
    this function loops open a file containing a directory listing that looks like:
    FILE\t<name>\t<?>\t<size>\t<?>\t<?>\t<?>\t<>\t<?>\t<cdate>\t<ctime>\t<mdate>\t<mtime>
    we stripe the first 
    """
    for line in open(filename,'r'):
        if line.startswith('FILE'):
            tokens = line.split('\t')
            fullpath = tokens[1]            
            size = int(tokens[3])
            dt = tokens[11]+' '+tokens[12]
            mtime =  datetime.datetime.strptime(dt.strip(),'%m/%d/%Y %H:%M:%S')
            yield (fullpath[n_ignore:], size, mtime)


def walk_folders(path, db, walker, path_ignore):
    n_ignore = len(path_ignore)
    old_root = None
    allfiles = []
    for fullpath, size, mtime in walker(path,n_ignore):
        allfiles.append(fullpath)
        root,filename = os.path.split(fullpath)
        print fullpath
        if root!=old_root:
            logging.info('processing folder '+root)
            old_root = root
            root_id=0
            for i in range(1,root.count('/')+2):
                folder = os.path.join(*root.split('/')[:i])
                parent = db(db.catalog_folder.path==folder).select().first()        
                if not parent:
                    logging.info('>>> creating folder '+folder)
                    meta_catalog_filename = os.path.join(folder,META_CATALOG)
                    if os.path.exists(meta_catalog_filename):
                        meta_catalog = parse_meta_catalog(meta_catalog_filename)
                        if 'nobody' in meta_catalog.get('access',[]): continue
                    else:
                        meta_catalog = Cataloger.build(folder)
                    title = meta_catalog.get('title',folder)
                    header = meta_catalog.get('header','')
                    footer = meta_catalog.get('footer','')
                    tags = meta_catalog.get('tags',[])
                    pattern_ignore = '^'+meta_catalog.get('ignore',PATTERN_IGNORE)+'$'
                    regex_ignore = re.compile(pattern_ignore)
                    pattern_group = meta_catalog.get('group',PATTERN_GROUP)
                    regex_group = re.compile(pattern_group)
                    root_id = db.catalog_folder.insert(
                        path=folder[:-1] if folder.endswith('/') else folder,
                        root_id=root_id,
                        title=title,
                        header=header,
                        footer=footer,
                        pattern_ignore=pattern_ignore,
                        pattern_group=pattern_group)
                    db.commit()
                    for tag in tags:
                        db.tag.insert(root_id=root_id,name=tag)                
                else:
                    root_id = parent.id 
                    pattern_ignore = parent.pattern_ignore
                    regex_ignore = re.compile(pattern_ignore)
            records = db(db.catalog_file.root_id==root_id).select()
        updated = False
        if filename!=META_CATALOG and not regex_ignore.match(filename):
            record = records.find(lambda row:row.filename==fullpath).first()
            # print record, (record.mtime if record else 'unkown')
            if not record or not record.size==size or record.mtime<mtime:
                logging.info('updating file '+filename)
                extension = regex_extension.search(filename) or ''
                tail = os.path.split(filename)[1]
                if extension:
                    tail = tail[:-len(extension and extension.group())]
                pattern = regex_group.sub('nnnnn',tail)
                db.catalog_file.insert(root_id=root_id,
                                       filename=fullpath,size=size,
                                       pattern = pattern,mtime=mtime,
                                       extension = extension and extension.group())
                db.commit()
                updated = True
        if not updated:
            logging.info('ignoring file '+filename)
    records = db(db.catalog_file).select()
    for record in records:
        if not record.filename in allfiles:
            logging.info('deleting file '+record.filename)
            db(db.catalog_file.id==record.id).delete()
        db.commit()
    return

def main(path):
    """
    from dal import DAL, Field
    db=DAL('sqlite://catalog.sqlite')
    db.define_table('catalog_folder',
                    Field('root_id','reference catalog_folder'),
                    Field('path'),
                    Field('title'),
                    Field('header','text'),
                    Field('footer','text'),
                    Field('pattern_ignore'),
                    Field('pattern_group'))
    db.define_table('tag',
                    Field('name'),
                    Field('root_id','reference catalog_folder'))
    db.define_table('catalog_file',
                    Field('root_id','reference catalog_folder'),
                    Field('filename'),
                    Field('md5'),
                    Field('pattern'),
                    Field('extension'),
                    Field('size','decimal(20,0)'),
                    Field('mtime','datetime'))
    db.define_table('attribute',
                    Field('catalog',db.catalog_file),
                    Field('name'),
                    Field('value','double'))
                    """
    if os.path.exists(path):
        if os.path.isdir(path):
            walk_folders(path,db,folder_walker,'')
        else:
            walk_folders(path,db,ls_walker,'/projects/qcd/')
    else:
        raise "Invalid path"
    for record in db(db.catalog_file).select():
        print record.root_id,record.filename,record.pattern,record.extension,record.size

main('applications/nersc/private/qcd_ls.txt')
