############################################
#You must hacve the same in controllers/sistemas.py

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






