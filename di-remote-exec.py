#!/usr/bin/python
import os,sys,paramiko
from threading import Thread,active_count
from time import sleep
from di_utils import target_info,print_host,async_out,async_err

username, password, hosts, cmds=target_info(sys.argv[1:])

def exec_cmd(host,cmds):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print '[%s] Connecting to %s ...'%(host,host)
	ssh.connect(host,22,username,password)
	for cmd in cmds:
		stdin,stdout,stderr=ssh.exec_command(cmd)
		t_out=async_out(host,stdout); t_err=async_err(host,stderr)
		t_out.join(); t_err.join()
	print_host(host,'Completed')
	ssh.close()

for host in hosts:
	t=Thread(target=exec_cmd,args=(host,cmds))
	t.setDaemon(True)
	t.start()
try:
	while True:
		s=active_count()
		if s>3:
			sleep(0.5)
		elif s==3 or s==2:
			sleep(0.1)
		else:
			break;
except(KeyboardInterrupt,SystemExit):
	sys.exit(1)