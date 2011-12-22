#!/usr/bin/python
# -*- coding: utf8 -*-
import time
import sqlite3
import commands

#Importamos las configuraciones
#Importamos las configuraciones
from conf import orca_path, path_systemd_server, ssh_user_admin, database_sqlite3, server_software, path_client_systemd

############################################

#Debe ser absoluta
#path_systemd_server="/media/STOREX/trabajo/Documents/GrandesInstlaciones/SystemD/server/web2py"
path_systemd_orca_server=path_systemd_server+'/'+orca_path
path_systemd_orca_client_database=path_client_systemd+"/databases/orca"
#############################################

#CONEXONES A BBDD
#############################################
#Conectamos a la BBDD con SQLLITE
#Se establece la conexion hasta su futuro cierre de la aplicacion
conn = sqlite3.connect(database_sqlite3)

print "Iniciado el demonio para Orca..."
################################################


class recolect_orca: 
    def Conectar(self):
	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	print "Este es el recolector de ORCA"
	#Conectamos a la BBDD
	platforms = conn.cursor()
	servers = conn.cursor()
	#Sacamos los datos de la BBDD
	print "Se establece conexión con la BBDD"
	platforms.execute('select id,name from platform')
	for platform in platforms:
	  print "############################################################"
	  print "Nombre de la plataforma: %s" %platform[1]
	  print "Identificador de la plataforma: %s" %platform[0]
	  servers.execute('select id, ip, port from server where id_platform='+str(platform[0]))
	  for server in servers:
	    print "----------------------------------------------------------"
	    print "Identificador del servidor: %s" %server[0]
	    print "IP del servidor: %s" %server[1]
	    print "Puerto de conexión SSH: %s" %server[2]
	    #Establecemos la conexion SSH para extrer datos del servidor
	    id_server=server[0]
	    ip_server=server[1]
	    port_server=server[2]
	
	    #Recupermos los dados generados por orca por medio de rsync
	    port="'ssh -p '" + str(port_server)
	    SyncCmd1 = 'rsync -arv -e '+port+' '+ ssh_user_admin+'@'+ip_server+':'+path_systemd_orca_client_database+'/*'+' '+path_systemd_orca_server+'/'+str(platform[0])+'/'+str(id_server)+'/'
	    SyncCmd2 = SyncCmd1+';'+ path_systemd_server+'/'+server_software+'/orca/bin/orca -no-html -once '+path_systemd_orca_server+'/'+str(platform[0])+'/'+str(id_server)+'/procallator.cfg'
	    print SyncCmd2
	    [status,output]=commands.getstatusoutput(SyncCmd2)
	    print SyncCmd2
	    print status
	    print output
	    

    def Ejecutar(self):
        while 1:
             self.Conectar()
             time.sleep(30)


def start():
    #Conexion para SQLlite
    hm1 = recolect_orca()
    hm1.Ejecutar()
