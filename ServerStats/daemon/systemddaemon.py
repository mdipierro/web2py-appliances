#!/usr/bin/python

# -*- coding: UTF8 -*-

###########################################################################
# configure these paths:

LOGFILE = '/var/log/systemd.log'
ERRORLOGFILE = '/var/log/systemd.err'
PIDFILE = '/var/run/systemd.pid'

# and let USERPROG be the main function of your project

import orcad
USERPROG = orcad.start


###########################################################################

#based on Jurgen Hermanns http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
import sys, os, time

class Log:
    # file like for writes with auto flush after each write to ensure that everything is logged,
    # even during an unexpected exit.

    def __init__(self, f):
        self.f = f

    def write(self, s):
        # Gracias a Nubio por este condicional!! 
        if s.strip() == '': return
        self.f.write('%s -- %s\n' % (time.ctime(), s))
        self.f.flush()

 

def main():
    #change to data directory if needed
    os.chdir("/")

    #redirect outputs to a logfile
    sys.stdout = Log(open(LOGFILE, 'a+'))
    sys.stderr = Log(open(ERRORLOGFILE, 'a+'))
    
    #ensure the that the daemon runs a normal user
    #set user and group first "pydaemon" 
    os.setegid(1000)
    os.seteuid(1000)

    #start the user program here:
    print "Starting daemon"
    USERPROG()
    print "Endding daemon"
 

if __name__ == "__main__":

    # do the UNIX double-fork magic
    # see "Stevens Advanced Programming in the UNIX Environment"
    # for details (ISBN 0201563177)

    try: 
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # decouple from parent environment and do not prevent unmounting
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            open(PIDFILE,'w').write("%d"%pid)
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # start the daemon main loop
    main()

start()