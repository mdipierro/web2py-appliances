# try something like
import datetime, os
today = request.now

db=SQLDB("sqlite://db.db")

db.define_table('line',
   SQLField('name'))
   
db.define_table('station',
   SQLField('name'))

db.define_table('departure',
   SQLField('line',db.line),
   SQLField('number','integer'),
   SQLField('station',db.station),
   SQLField('time','integer'),
   SQLField('weekday','boolean'),
   SQLField('saturday','boolean'),
   SQLField('sunday','boolean'))
   

db.define_table('arrival',
   SQLField('line',db.line),
   SQLField('number','integer'),
   SQLField('station',db.station),
   SQLField('time','integer'),
   SQLField('weekday','boolean'),
   SQLField('saturday','boolean'),
   SQLField('sunday','boolean'))
   
db.executesql('CREATE INDEX IF NOT EXISTS arrival_number_idx ON arrival(number);')
db.executesql('CREATE INDEX IF NOT EXISTS arrival_station_idx ON arrival(station);')
db.executesql('CREATE INDEX IF NOT EXISTS departure_number_idx ON departure(number);')
db.executesql('CREATE INDEX IF NOT EXISTS departure_station_idx ON departure(station);')

backup_filename = os.path.join(request.folder,'backup.csv')
if db(db.station).isempty():
    db.import_from_csv_file(open(backup_filename,'rb'))
elif not os.path.exists(backup_filename):
    db.export_to_csv_file(open(backup_filename,'wb'))

if len(db().select(db.station.ALL))==0:
    import cPickle, os
    data=cPickle.load(open(os.path.join(request.folder,
                                        'metra.pickle'),'r'))
    lines={}
    stations={}
    for line,i,routes in data:
        if not lines.has_key(line): lines[line]=db.line.insert(name=line)
        wd,sa,su=(i==1),(i==2),(i==3)
        for number,route in routes.items():
            k=0
            for station,t in route:
                if not stations.has_key(station):
                    stations[station]=db.station.insert(name=station)
                this=dict(line=lines[line],number=number,station=stations[station],\
                          time=t,weekday=wd,saturday=sa,sunday=su)
                if k>0: db.arrival.insert(**this)                 
                if k<len(route)-1: db.departure.insert(**this)
                k+=1

lines=db().select(db.line.id,db.line.name,cache=(cache.ram,24*3600))
lines=dict([(x.id,x.name) for x in lines])
stations=db().select(db.station.ALL,cache=(cache.ram,24*2600))
stations=dict([(x.id,x.name) for x in stations])
