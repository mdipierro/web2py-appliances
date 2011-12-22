import re, urllib, sys, cPickle

metra_pages={
'Union Pacific North Line':[
('http://www.metrarail.com/Sched/cnw_n/cnwn_wki.shtml',1),
('http://www.metrarail.com/Sched/cnw_n/cnwn_wko.shtml',1),
('http://www.metrarail.com/Sched/cnw_n/cnwn_sai.shtml',2),
('http://www.metrarail.com/Sched/cnw_n/cnwn_sao.shtml',2),
('http://www.metrarail.com/Sched/cnw_n/cnwn_sui.shtml',3),
('http://www.metrarail.com/Sched/cnw_n/cnwn_suo.shtml',3)],
'North Central Service':[
('http://www.metrarail.com/Sched/ncs/ncs_wkin.shtml',1),
('http://www.metrarail.com/Sched/ncs/ncs_wkout.shtml',1)],
'Milwakee District North Line':[
('http://www.metrarail.com/Sched/md_n/mdn_wki.shtml',1),
('http://www.metrarail.com/Sched/md_n/mdn_wko.shtml',1),
('http://www.metrarail.com/Sched/md_n/mdn_sai.shtml',2),
('http://www.metrarail.com/Sched/md_n/mdn_sao.shtml',2),
('http://www.metrarail.com/Sched/md_n/mdn_sui.shtml',3),
('http://www.metrarail.com/Sched/md_n/mdn_suo.shtml',3)],
'Union Pacific Northest Line':[
('http://www.metrarail.com/Sched/cnw_nw/cnwnwwi.shtml',1),
('http://www.metrarail.com/Sched/cnw_nw/cnwnwwo.shtml',1),
('http://www.metrarail.com/Sched/cnw_nw/cnwnw6i.shtml',2),
('http://www.metrarail.com/Sched/cnw_nw/cnwnw6o.shtml',2),
('http://www.metrarail.com/Sched/cnw_nw/cnwnw7i.shtml',3),
('http://www.metrarail.com/Sched/cnw_nw/cnwnw7o.shtml',3)],
'Milwakee District West Line':[
('http://www.metrarail.com/Sched/md_w/mdw_wki.shtml',1),
('http://www.metrarail.com/Sched/md_w/mdw_wko.shtml',1),
('http://www.metrarail.com/Sched/md_w/mdw_sai.shtml',2),
('http://www.metrarail.com/Sched/md_w/mdw_sao.shtml',2),
('http://www.metrarail.com/Sched/md_w/mdw_sui.shtml',3),
('http://www.metrarail.com/Sched/md_w/mdw_suo.shtml',3)],
'Union Pacific West Line':[
('http://www.metrarail.com/Sched/cnw_w/cnwwwki.shtml',1),
('http://www.metrarail.com/Sched/cnw_w/cnwwwko.shtml',1),
('http://www.metrarail.com/Sched/cnw_w/cnwwsai.shtml',2),
('http://www.metrarail.com/Sched/cnw_w/cnwwsao.shtml',2),
('http://www.metrarail.com/Sched/cnw_w/cnwwsui.shtml',3),
('http://www.metrarail.com/Sched/cnw_w/cnwwsuo.shtml',3)],
'BNSF Railway Line':[
('http://www.metrarail.com/Sched/bn/bn_wki.shtml',1),
('http://www.metrarail.com/Sched/bn/bn_wko.shtml',1),
('http://www.metrarail.com/Sched/bn/bn_sati.shtml',2),
('http://www.metrarail.com/Sched/bn/bn_sato.shtml',2),
('http://www.metrarail.com/Sched/bn/bn_suni.shtml',3),
('http://www.metrarail.com/Sched/bn/bn_suno.shtml',3)],
'Heritage Corridor':[
('http://www.metrarail.com/Sched/mhc/mhc_all.shtml',1)],
'Southwest Service':[
('http://www.metrarail.com/Sched/sws/sws_all.shtml',1)],
'Rock Island District Line':[
('http://www.metrarail.com/Sched/ri/ri_wki.shtml',1),
('http://www.metrarail.com/Sched/ri/ri_wko.shtml',1),
('http://www.metrarail.com/Sched/ri/ri_sai.shtml',2),
('http://www.metrarail.com/Sched/ri/ri_sao.shtml',2),
('http://www.metrarail.com/Sched/ri/ri_sui.shtml',3),
('http://www.metrarail.com/Sched/ri/ri_suo.shtml',3)],
#'Metra Electric Line':[
#('http://www.metrarail.com/Sched/me/me_msi.shtml',1),
#('http://www.metrarail.com/Sched/me/me_mso.shtml',1),
#('http://www.metrarail.com/Sched/me/me_msi.shtml',2),
#('http://www.metrarail.com/Sched/me/me_mso.shtml',2),
#('http://www.metrarail.com/Sched/me/me_sui.shtml',3),
#('http://www.metrarail.com/Sched/me/me_suo.shtml',3)]
}

def parse(page):
    stop=0
    routes={}
    nn=len('Kenosha (WI)        LV')
    while 1:
        start=page.find('<pre><h4>',stop)
        if start<0: break
        stop=page.find('<hr',start)
        if stop<0: break
        table=page[start+9:stop]
        k=0 
        stations=[]
        for line in re.compile('<.+?>').sub(' ',table).split('\n'):
            if not line.strip(): continue
            if k==0:
                numbers=re.compile('\d+').findall(line)
                for number in numbers: routes[number]=[]
            elif k==1:
                ampm=re.compile('(AM|PM)').findall(line)
            else:
                name=re.sub('\s+',' ',line[:nn].strip())
                stations.append(name)
                times=re.compile('[\d\:\.]+|[\-]+|[\|]').findall(line[nn:])
                for i,x in enumerate(times):
                    if not x in ['|','----','-','--','---']:
                        h,m=x.split(':') if x.find(':')>0 else  x.split('.')
                        t=int(h)*60+int(m)
                        if ampm[i].lower()=='pm' and not int(h)==12: t+=12*60
                        elif ampm[i].lower()=='am' and int(h)==12: t+=12*60
                        t=t%(24*60)
                        routes[numbers[i]].append((name,t))
            k+=1
    return routes

if __name__=='__main__':
     obj=[]
     for line,items in metra_pages.items():
         for item in items:
             print line, item
             page=urllib.urlopen(item[0]).read()
             obj.append((line,item[1],parse(page)))
             cPickle.dump(obj,open('metra.pickle','w'))
