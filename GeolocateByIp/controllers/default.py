if not session.ip:
	try:
		ip = request.env.remote_addr
		data = geoip(ip)
		if data: session.data = B(IMG(_src=URL(r=request, c="static", f="flags/" + data[1].lower() + ".png"), _alt="geoip flag", _style="margin-bottom: -4px"), B(data[0] + " (" + data[1] + ")"))
		else: raise ValueError
	except: session.data = B("Unknown")
	session.ip = ip

def download():
	from os import stat
	from os.path import join
	try:
		if stat(join("applications", request.application, "databases", "geoip.db"))[6] <> 0L: redirect(URL(r=request, f="index"))
	except: pass
	from cStringIO import StringIO
	from urllib import urlopen
	from zipfile import ZipFile
	from sqlite3 import connect

	connection = connect(join("applications", request.application, "databases", "geoip.db"))
	cursor = connection.cursor()
	cursor.execute("create table geoip (id integer primary key autoincrement, begin_ip char(15), end_ip char(15), begin_num integer, end_num integer, code char(2), name char(32))")
	data = ZipFile(StringIO(urlopen("http://www.maxmind.com/download/geoip/database/GeoIPCountryCSV.zip").read()))
	data = StringIO(data.read(data.namelist()[0]))
	while True:
		chunk = data.readline()
		if not chunk: break
		cursor.execute("insert into geoip (begin_ip, end_ip, begin_num, end_num, code, name) values (" + chunk + ")")
	connection.commit()
	cursor.close()
	return dict()

def installation():
	from os import unlink
	from os.path import join
	try: unlink(join("applications", request.application, "databases", "geoip.db"))
	except: pass
	return dict()

def index():
	from os import stat
	from os.path import join
	try:
		if stat(join("applications", request.application, "databases", "geoip.db"))[6] == 0L: raise ValueError
	except: redirect(URL(r=request, f="installation"))
	if len(request.args):
		ip = request.args[0]
		if ip == "random":
			from random import randint as R
			ip = ".".join(map(str, (R(0, 255), R(0, 255), R(0, 255), R(0, 255))))
		try:
			data = geoip(ip)
			if data: session.data = session.data = B(IMG(_src=URL(r=request, c="static", f="flags/" + data[1].lower() + ".png"), _alt="geoip flag", _style="margin-bottom: -4px"), B(data[0] + " (" + data[1] + ")"))
			else: session.data = B("Unknown")
		except: redirect(URL(r=request, f="index"))
		session.ip = ip
	form = FORM(
		B("Address: "),
		INPUT(_type="text", _name="ip", _value=session.ip, _size="15", _maxlength="15", requires=IS_MATCH("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")),
		INPUT(_type="submit",_value="Locate"),
		" ",
		A("random", _href=URL(r=request, c="default", f="index/random")),
		BR(),
		BR(),
		session.data)
	if form.accepts(request, keepvalues=True):
		session.ip = request.vars.ip
		data = geoip(session.ip)
		if data: session.data = session.data = B(IMG(_src=URL(r=request, c="static", f="flags/" + data[1].lower() + ".png"), _alt="geoip flag", _style="margin-bottom: -4px"), B(data[0] + " (" + data[1] + ")"))
		else: session.data = B("Unknown")
		redirect(URL(r=request, f="index"))
	elif form.errors:
		form.errors.clear()
		response.flash = "Invalid IPv4 address"
	return dict(form = form)