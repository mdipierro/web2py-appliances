#!/usr/bin/env python
# coding: utf8
from gluon import *
from jsonrpc import ServiceProxy
import re
import subprocess
#access is a Server Proxy object between web2py and the command
#line program bitcoind using the session variables you supplied
#in the index page

def start_bitcoin():
    s = subprocess
    s.Popen(["bitcoind", "-server"], stdin=s.PIPE, stdout = s.PIPE, stderr=s.PIPE, close_fds=True)
    return dict( True=True)

start_bitcoin()
domain = '127.0.0.1'
port = '8332'
s = "http://" + "cstclair" + ":" + "BilboBaggins133" + "@" + domain + ":" + port
access = ServiceProxy(s)
#creates a new bitcoin address with your desired username you provided 
#or your existing account if found in your wallet file
def backupwallet(location):
    #backs up your wallet file in a directory of your choosing
    if(isinstance(location, str)):
        regex = re.compile('^(.+)/([^/]+)$') #regex for a UNIX directory- sorry Windows...
        if(re.match(regex, location) is not None): 
            access.backupwallet(location)
            return dict()
        else:
            return dict(error="invalid path name")
    else:
        return dict(error="invalid path name")
        
def encryptwallet(passphrase):
    #encrypts your wallet file with a (strong) passphrase
    if(isinstance(passphrase, str)):
        regex = re.compile('(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$')
        if(re.match(regex, passphrase) is not None):
             access.encryptwallet()
             return dict()
        else:
            error = 'error3'
            return dict(error="Passphrase must contain at least 8 characters total, at least one uppercase letter, one lower case, and one number or special character")
            

def getaddress(account):
    #returns you your current bitcoin address mapped to your account
    #bitcoin address can be 25-34 characters in length
    address = access.getaccountaddress(account)
    return dict(address=address)

def getaddressesbyaccount(account):
    #returns you multiple bitcoin addresses if you have multiple addresses
    addressList = access.getaddressesbyaccount(account)
    stringaddressList = []
    i = 0
    for address in addressList:
        stringaddressList[i] = str(address)
        i = i + 1
    return dict(stringaddressList=stringaddressList)
        
def getblocknumber():
    #returns your block number
    try:
        blocknum = access.getblocknumber()        
        return dict(blocknum = blocknum)
    except:
        return dic("error","could not get block number")
    
def getbitcoininfo():
    #returns a dictionary with your bitcoin info
    try:
        info = access.getinfo()
        return dict(info=info)
    except:
        return dict("error", "could not get info")
    
def getconnectioncount():
    #returns the amount of nodes you are connected to 
    try:
        connect = access.getconnectioncount()
        return dict(connect=connect) 
    except:
        return dict(error="could not get connection count")
    
def getdifficulty():
    #gets difficulty of the problem your machine is working on
    #as more bitcoins are mined, the difficulty rises
    try:
        diff = int(access.getdifficulty())
        return dict(diff=diff)   
    except:
        return dict(error="could not get difficulty")
       
def getnewaddress():
    #returns you a new address linked to your accountname
    address = access.getnewaddress(auth.user)
    return dict()       
       
def getwork():
    #return information on work done by your bitcoin client
    #the proxy function breaks often enough that it needed
    #to be wrapped in a try/except block
    try:
        work = access.getwork()
        return dict(work=work)
    except:
        return dict()    
        
def generatecoins():
    #starts your bitcoin miner 
    if(not access.getgenerate()):
        access.setgenerate(True)
    return dict()
    
def dontgenerate():
    #stops your bitcoin miner
    if(access.getgenerate()):
        access.setgenerate(False)
    return dict()

def send(address, amount):
    #send bitcoin and amount
    try:
        access.sendtoaddress(address, amount)
        return dict()
    except:
        #it's probably working, regardless of whether or not the session
        #timed out
        return dict()
    
def getbalance():
    #returns you your bitcoin balance
    bal = float(access.getbalance())
    return dict(bal=bal)
    
def getrecievedbyaccount(account):
    #tells you how many bitcoins you recieved per account
    if(isinstance(account, str)):
        amount = float(getrecievedbyaccount(account))
        return dict(amount=amount)
    else:
        return dict("error","not a valid account")
    
def listaccounts():
    #list accounts in your wallet file
    return access.listaccounts()
    
def settxfee(amount):
    #set your tax fee for a transaction
    #should be between 0 and 0.99
    if(not (isinstance(amount, float))):
        return dict("error","amount is not a float")
    elif(amount > 0.99):
        return dict("error","can't be more than 99%")
    else:
        access.settxfee(amount)
    return dict()
        
def validate(address):
    #returns true if the bitcoin address is valid; false otherwise
    #valid bitcoin address are between 25-34 upper, lower chars and numbers
    address = access.validateaddress(address)
    regex = re.compile('([a-z]|[A-Z]|[0-9]){24,35}')
    if(re.match(regex, address) is not None):    
        return True
    return False

def stop():
    #stop the bitcoin server
    #if you run this, all the other methods will break
    access.stop()
    return dict(message="stopped")
