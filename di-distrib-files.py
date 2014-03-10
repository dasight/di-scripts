#!/usr/bin/python
import os,sys,paramiko
from threading import Thread
from glob import glob
from di_utils import target_info,print_host

username, password, hosts, para=target_info(sys.argv[1:])
src={}
for i in para[0:-1]:
	for f in glob(i):
		k=f.split('/')[-1]
		if k in src:
			print 'File name duplication: '+k
		else:
			src[k]=f

def copy_file(host,src,des):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print '[%s] Connecting to %s ...'%(host,host)
	ssh.connect(host,22,username,password)
	sftp=ssh.open_sftp()
	print_host(host,'Connected. Start transferring ...')
	for sn,fn in src.items():
		sftp.put(fn,des+'/'+sn)
		print_host(host,fn+' copied')
	print_host(host,'Completed')
	ssh.close()

threads=[]
for host in hosts:
	t=Thread(target=copy_file,args=(host,src,para[-1]))
	t.start()
	threads.append(t)
for t in threads:
	t.join()