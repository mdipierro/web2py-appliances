from re import compile

db=DAL('sqlite://geoip.db')

db.define_table("geoip",
	Field("begin_ip", "string", length=15),
	Field("end_ip", "string", length=15),
	Field("begin_num", "integer"),
	Field("end_num", "integer"),
	Field("code", "string", length=2),
	Field("name", "string"), migrate=False)

def geoip(address):
	address = str(address)
	if not compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$").match(address): raise ValueError, "Invalid IPv4 address"
	address = map(int, address.split("."))
	value = 16777216 * address[0] + 65536 * address[1] + 256 * address[2] + address[3]
	rows = db((db.geoip.begin_num <= value) & (db.geoip.end_num >= value)).select()
	if rows:
		rows = rows[0]
		return (rows.name, rows.code, rows.begin_ip, rows.end_ip)
	else: return None