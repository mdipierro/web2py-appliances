# coding: utf8
# try something like
import os, shlex, subprocess

############################################
#You must hacve the same in daemon/conf.py

#Absolute path to the server web2py
path_systemd_server="/opt/web2py"
#Relative path from the server to the application software
client_software='applications/serverStatistics/software/client'
server_software='applications/serverStatistics/software/server'
#Admin user configuration access
ssh_user_admin='root'
rsa_private_key_admin=r"/root/.ssh/id_rsa" # r is needed
#Another user without privileges (not dev yet)
ssh_user='none'
rsa_private_key=r"none"
#Relative path to the database orca (where the graphs are stored)
orca_path='applications/serverStatistics/orca'
#Where we want to install orca in the client
path_client_systemd='/opt/systemd'
#Relative path to the database
database_sqlite3='applications/serverStatistics/databases/serverStatistics.db'



def index():
    return dict(message="Portal de aminitración de SystemD")

def orca():
    import glob
    server_id=request.post_vars.server
    platform_id=request.post_vars.platform
    filter_id=request.post_vars.filter
    time=request.post_vars.time

    print "Filtro seleccionado: %s"% (filter_id)
    print "Servidor seleccionado: %s"% (server_id)
    print "Horario de grafica: %s"% (time)
    print os.system('pwd')
    print "Plataforma seleccionado: %s"% (platform_id)


    if (server_id=="undefined" and platform_id=="undefined" and filter_id=="undefined"):
	  response.flash = T('Welcome SystemD')
    else:
      try: 
	  type_graphs= orcadb((orcadb.grupo_graph.id_grupo==filter_id) & (orcadb.type_graph.id==orcadb.grupo_graph.id_type_graph))
      except:
	  print "Error"
      
      imagesdb={}
      imagesdb_name={}
      imagesdb_description={}
      count=0
      aplication=request.application
      
      platform_id_str=str(platform_id)
      server_id_str=str(server_id)
      for type_graph in type_graphs.select():
	filter=type_graph.type_graph.filter
	name=type_graph.type_graph.name
	description=type_graph.type_graph.description
	print filter
	path=orca_path+'/'+platform_id_str+'/'+server_id_str+'/img/*'+filter+time+'.png'
	print path
	for filename in glob.glob(path):
	    data = open(filename, "rb").read()
	    imagesdb[count]=data
	    imagesdb_name[count]=name
	    imagesdb_description[count]=description
	    count = count + 1
  
    print "Graphs Number: %s" % (count)  


    return dict(time=time,server_id=server_id,platform_id=platform_id,filter_id=filter_id,imagesdb=imagesdb, imagesdb_name=imagesdb_name,imagesdb_description=imagesdb_description)
    

def select_servers_platform():
    platform_id=request.post_vars.platform
    servers=systemd(systemd.server.id_platform==platform_id).select(orderby=systemd.server.name)
    return dict(servers=servers)
   
 
    
def edit_server():    
    server_id=request.args(0)
    server=systemd.server[server_id] #or redirect(error_page)
    form=crud.update(systemd.server,server,next=url('list_server'))
    return dict(form=form)
    
    
def view_server():
    server_id=request.args(0)
    server=systemd.server[server_id] #or redirect(error_page)    
    return dict(server=server)
    
    
def list_platform():
    if request.post_vars:
        form1=crud.create(systemd.server)
        form2=crud.create(systemd.platform)
        platforms=systemd(systemd.platform.id>0).select(orderby=systemd.platform.name)
        display="yes"
    else:
        form1=crud.create(systemd.server)
        form2=crud.create(systemd.platform)
        platforms=systemd(systemd.platform.id>0).select(orderby=systemd.platform.name)
        display="none"
         
    return dict(platforms=platforms, form1=form1, form2=form2, display=display)
    

def list_server():
    #To use ssh client
    import paramiko
    display_server="none"
    display_platform="none"
    servers=None
    form1=None
    form2=None
    try:
      form1=crud.create(systemd.server)
      form2=crud.create(systemd.platform)
    except Exception,e:
      print 'BBDD bloqueda por el demonio'
      return '<span style="color:red;">Maybe DDBB is BLOCKED by the deamon</span>'
    #print request.post_vars
    if request.post_vars._formname=='server/None':
        display_server="yes"
	#Creamos Estructura para orca. Esta es por mendio de los IDs
	#Se extrae el ultimo servidor introducido para hacer las configuraciones
	server=systemd().select(systemd.server.id,systemd.server.ip, systemd.server.port,orderby=~systemd.server.id,limitby=(0,1))
	last_server=server[0].id
	ip_server=server[0].ip
	port_server=server[0].port
	platform=request.post_vars.id_platform
	path_server=orca_path+'/'+str(platform)+'/'+str(last_server)
	path_server_img=orca_path+'/'+str(platform)+'/'+str(last_server)+'/img'
	
	try: 
	  os.makedirs(path_server_img)
	  
	  try:
	    #Open de file to make some change for config this server
	    orca_conf = open(server_software+'/orca/etc/procallator.cfg','r');
	    orca_conf_orig=orca_conf.read();
	    orca_conf.close();

	  except (RuntimeError, TypeError, NameError, IOError):
	    print ('Error en la ubicacion o nombre del archivo');
	  #Modifica la cadena del texto original del archivo
	  if orca_conf_orig.find("change_text_1") >= 0:
	    orca_conf_aux1 = orca_conf_orig.replace('change_text_1',path_systemd_server+'/'+path_server);
	  if orca_conf_aux1.find("change_text_2") >= 0:
	    orca_conf_aux2 = orca_conf_aux1.replace('change_text_2',path_systemd_server+'/'+path_server_img);
	  if orca_conf_aux2.find("change_text_3") >= 0:  
	    orca_conf_new = orca_conf_aux2.replace('change_text_3',path_systemd_server+'/'+path_server);
	    #Abre el archivo para escritura de datos
	    new_file_conf = open(path_server+'/procallator.cfg','w');
	    new_file_conf.writelines(orca_conf_new);
	    new_file_conf.close();
	    print ('We chage the original text');
	  else:
	    print ('No se encontro el texto buscado en el texto original. ');
	    print ('No se realizo ningun cambio.');
	
	  #Se compia por ssh el sistema Cliente compuesto por Orca y Awstat
	  #It's posible not compatible with Google App Engine
	    
	  #We make the copy of the software
	  os.system('scp -r -P'+str(port_server)+' '+client_software+' '+ssh_user_admin+'@'+str(ip_server)+':'+path_client_systemd+';'+'scp -P'+str(port_server)+' '+client_software+'/bin/S99procallator '+ssh_user_admin+'@'+str(ip_server)+':/etc/rc3.d/')

	  #It doesnt work, I didnt checked
	  
	  #conexion = paramiko.SSHClient()
	  #conexion.load_system_host_keys()
	  #conexion.connect(ip_server, port_server, username = ssh_user_admin, key_filename = rsa_private_key_admin)
	  #stdin, stdout, stderr = conexion.exec_command('/etc/rc3.d/S99procallator start')
	  #result=stdout.read()
	  #print result
	  #conexion.close()
      
	except:
	  print 'Se ha producido un error en la instalacion de ORCA'
	  return '<span style="color:red;">Proble with ORCA instaltion.</span>'
	  

    elif request.post_vars._formname=='platform/None':
        display_platform="yes"
    
    servers=systemd(systemd.server.id>0).select(orderby=systemd.server.name)
    
    return dict(servers=servers, form1=form1, form2=form2, display_server=display_server, display_platform=display_platform)
    
def server_health():
    servers=None
    platform_id=request.post_vars.platform
    print platform_id
    platform=systemd.platform[platform_id]
    if platform:
        servers=systemd(systemd.server.id_platform==platform_id).select(orderby=systemd.server.name)

    platforms=systemd(systemd.platform.id>0).select(orderby=systemd.platform.name)
    servers=systemd(systemd.server.id>0).select(orderby=systemd.server.name)
    graphs=orcadb(orcadb.type_graph.id>0).select(orderby=orcadb.type_graph.name)
    groups=orcadb(orcadb.grupo.id>0).select(orderby=orcadb.grupo.name)
    
    return dict(platforms=platforms, servers=servers, graphs=graphs, groups=groups)


def server_health_options():
    form=crud.create(orcadb.grupo_graph)
    return dict(form=form) #For jquery view
    #return form #For ajax


def platform_statistics():
    platforms=systemd(systemd.platform.id>0).select(orderby=systemd.platform.name)
    
    return dict(platforms=platforms)


def test_server_view():
  return dict(servers=systemd().select(systemd.server.ALL))

#Funcion para probar si es accesible todos los servidores y si el proceso esta levantado
def test_port_ssh():
    import socket
    import sys
    server_id=request.args[0]
    server=systemd(systemd.server.id==server_id).select(systemd.server.name, systemd.server.ip, systemd.server.port)
    #server=systemd(systemd.server.id==server_id).select().ALL
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60)
    try:
	sock.connect((server[0].ip, server[0].port))
    except Exception,e:
	#print "%s closed " % (server[0].port)
	return '<span style="color:red;">FAIL</span>'

    else:
	return '<span style="color:green;">OK</span>'
	
    sock.close()        

def test_connect_ssh():
  import sys, paramiko
  server_id=request.args[0]
  server=systemd(systemd.server.id==server_id).select(systemd.server.name, systemd.server.ip, systemd.server.port)
  conexion = paramiko.SSHClient()
  conexion.load_system_host_keys()
  
  try:
    conexion.connect(server[0].ip, server[0].port, username = ssh_user_admin, key_filename = rsa_private_key_admin)
    #stdin, stdout, stderr = conexion.exec_command('echo "conectado..."')
    
    
  except Exception,e:
    return '<span style="color:red;">FAIL</span>'
    conexion.close()
  else:
    #Only tested on Linux, maybe works for Solaris
    #stdin, stdout, stderr = conexion.exec_command('ps -ef | grep procallator | grep -v grep | awk {'+"'"+'print $2'+"'"+'}')
    stdin, stdout, stderr = conexion.exec_command('ps -e')
    result=stdout.read()
    conexion.close()

    if result:
      message='ORCA running'
    else:
      message='<span style="color:red;">ORCA stoped</span>'

    return '<span style="color:green;">OK, '+message+'</span>'

  
  
def config_system():
  #Lets see if SystemD daemon is working
  hola = "hola"
  return dict(hola=hola)

def check_services_systemd():
  import commands
  data=request.args[0]
  if data == "orca":
    #result=commands.getoutput('ps -ef | grep systemddaemon | grep -v grep | grep -v "ps -ef"')
    result=commands.getoutput('ps -e')
    if "systemddaemon" in result:
      return '<span style="color:green;">OK</span>'
    else:
      return '<span style="color:red;">STOPED</span>'
      
  if data == "start":
     #result=commands.getoutput('ps -ef | grep systemddaemon | grep -v grep | grep -v "ps -ef"')
     result=commands.getoutput('ps -e')
     if "systemddaemon" in result:
      return '<span style="color:green;">LOOKS OK</span>'
     else:
      os.system('applications/%s/daemon/systemddaemon.py' %request.application)
      return '<span style="color:green;">OK</span>'
   
  if data == "stop":
      return '<span style="color:red;">NOT DEV</span>'
      

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())




def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
