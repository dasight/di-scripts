#!/usr/bin/python
import os,sys,paramiko
from threading import Thread
from getopt import getopt,GetoptError

try:
	opts,hosts=getopt(sys.argv[1:],'u:p:c:')
except GetoptError:
	print("Syntax error")
	sys.exit(1)
username=None
password=None
cluster=None
for o in opts:
	if o[0]=='-u':
		username=o[1]
	elif o[0]=='-p':
		password=o[1]
	elif o[0]=='-c':
		cluster=o[1]
if username is None:
	print "Username not set, using 'root' by default"
	username='root'
if password is None:
	from getpass import getpass
	password=getpass('Password: ')

if not hosts:
	if cluster is None:
		cluster='default'
	f=open('/etc/hosts')
	hosts={}
	for line in f:
		linex=line.strip()
		if linex<>'' and not linex.startswith('#'):
			s=linex.split()
			if len(s)==3 and s[2].startswith('#hadoop_'+cluster):
				hosts[s[1]]=s[0]
	f.close()
	
	print 'Sync hostnames to the following hosts:'
	for k in sorted(hosts):
		print '\t%s\t%s'%(hosts[k],k)
	while True:
		s=raw_input('Continue (yes/no)? ')
		if s=='yes':
			hosts=hosts.keys()
			break
		elif s=='no':
			sys.exit(1)
	
def print_host(host,s):
	print '[%s] %s'%(host,s)
	
def sync_hostnames(host):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print '[%s] Connecting to %s ...'%(host,host)
	ssh.connect(host,22,username,password)
	print_host(host,'Connected')
	sftp=ssh.open_sftp()
	print_host(host,'Reading and processing '+host+':/etc/sysconfig/network ...')
	f=sftp.file('/etc/sysconfig/network','r+')
	netconf=''; revised=False
	for line in f.readlines():
		linex=line.strip()
		if linex<>'' and not linex.startswith('#'):
			s=[e.strip() for e in linex.split('=')]
			if s[0]=='HOSTNAME' and s[1]<>host:
				netconf+='# '+line
				netconf+='HOSTNAME='+host+'\n'
				revised=True
				break
		netconf+=line
	if revised:
		print_host(host,'Updating to /etc/sysconfig/network ...')
		f.seek(0)
		f.write(netconf)
		f.truncate(len(netconf))
		f.flush()
		print_host(host,'Updated')
	else:
		print_host(host,'Nothing to be updated')
	f.close()
	print_host(host,'Updating /etc/hosts ...')
	sftp.put('/etc/hosts','/etc/hosts')
	print_host(host,'Updated')
	ssh.close()
	print_host(host,'Sync DONE')
		
threads=[]
for host in hosts:
	t=Thread(target=sync_hostnames,args=(host,))
	t.start()
	threads.append(t)
for t in threads:
	t.join()