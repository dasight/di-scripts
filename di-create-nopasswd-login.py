#!/usr/bin/python
import os,sys,paramiko
from threading import Thread
from getopt import getopt,GetoptError

try:
	opts,hosts=getopt(sys.argv[1:],'u:p:')
except GetoptError:
	print("Syntax error")
	sys.exit(1)
username=None
password=None
for o in opts:
	if o[0]=='-u':
		username=o[1]
	elif o[0]=='-p':
		password=o[1]
if username is None:
	print "Username not set, using 'root' by default"
	username='root'
if password is None:
	from getpass import getpass
	password=getpass('Password: ')
if not hosts:
	f=open('hosts')
	for line in f:
		line=line.strip()
		if line<>'' and not line.startswith('#'):
			hosts.append(line.split()[1])
	f.close()
home=os.popen('echo $HOME').read().strip()
	
def print_host(host,s):
	print '[%s] %s'%(host,s)
	
def home_dir(host):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host,22,username,password)
	stdin,stdout,stderr=ssh.exec_command('echo $HOME')
	home=stdout.read().strip()
	ssh.close()
	return home
	
def gen_rsa_keys(host):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print '[%s] Connecting to %s ...'%(host,host)
	ssh.connect(host,22,username,password)
	print_host(host,'Connected')
	print_host(host,'Trying to remove previously generated RSA keys if existed')
	ssh.exec_command('rm -f ~/.ssh/id_rsa ~/.ssh/id_rsa.pub ~/.ssh/id_rsa.pub.all')
	print_host(host,'DONE')
	print_host(host,'Invoking ssh-keygen ...')
	stdin,stdout,stderr=ssh.exec_command("ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ''")
	for line in stdout.readlines():
		print_host(host,line.strip())
	print_host(host,'RSA keys generated')
	stdin,stdout,stderr=ssh.exec_command('echo $HOME')
	ssh.close()
	
	print_host(host,'Fetching id_rsa.pub ...')
	ssh=paramiko.Transport((host,22)) 
	ssh.connect(username=username,password=password) 
	sftp=paramiko.SFTPClient.from_transport(ssh) 
	sftp.get(home+'/.ssh/id_rsa.pub',home_dir(host)+'/.ssh/id_rsa.pub.'+host)
	ssh.close()
	print_host(host,'Fetching DONE')

def merge_rsa_keys():
	for host in hosts:
		ret=os.system('cat ~/.ssh/id_rsa.pub.'+host+' >> ~/.ssh/id_rsa.pub.all')
		if(ret<>0):
			print '[MAIN] Error when merging '+host+"'s RSA key"
			sys.exit(1)
	print '[MAIN] RSA keys merged'
	
def dist_rsa_keys(host):
	print_host(host,'Distributing id_rsa.pub to '+host)
	ssh=paramiko.Transport((host,22)) 
	ssh.connect(username=username,password=password) 
	sftp=paramiko.SFTPClient.from_transport(ssh) 
	sftp.put(home+'/.ssh/id_rsa.pub.all',home_dir(host)+'/.ssh/authorized_keys')
	ssh.close()
	print_host(host,'Distributing DONE')
	
def run(func):
	threads=[]
	for host in hosts:
		t=Thread(target=func,args=(host,))
		t.start()
		threads.append(t)
	for t in threads:
		t.join()
		
run(gen_rsa_keys)
merge_rsa_keys()
run(dist_rsa_keys)
