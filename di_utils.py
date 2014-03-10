#/usr/bin/python
import sys
from threading import Thread
from getopt import getopt,GetoptError

def fetch_hosts(cluster,hosts):
	if hosts is None:
		f=open(sys.path[0]+'/conf/hosts')
		hosts=[]
		for line in f:
			linex=line.strip()
			if linex<>'' and not linex.startswith('#'):
				s=linex.split()
				if len(s)==3 and s[2].startswith('#hadoop_'+cluster):
					hosts.append(s[1])
		f.close()
	return hosts

def target_info(args):
	try:
		opts,para=getopt(args,'yu:p:c:h:f:')
	except GetoptError:
		print("Syntax error")
		sys.exit(1)
	username=None
	password=None
	cluster=None
	hosts=None
	ks=False
	for o in opts:
		if o[0]=='-u':
			username=o[1]
		elif o[0]=='-p':
			password=o[1]
		elif o[0]=='-c':
			hosts=fetch_hosts(o[1],hosts)
		elif o[0]=='-h':
			hosts=[h.strip() for h in o[1].split(',')]
		elif o[0]=='-y':
			ks=True
		elif o[0]=='-f':
			if para is None:
				para=[line.strip() for line in open(o[1]).readlines()]
			else:
				print 'Conflict argument: -f'
				sys.exit(1)
	if username is None:
		print "Username not set, using 'root' by default"
		username='root'
	if password is None:
		from getpass import getpass
		password=getpass('Password: ')
	if hosts is None:
		print 'Please specify host names or a cluster name'
		sys.exit(1)

	print 'Targeting hosts are:',
	for k in sorted(hosts):
		print k,
	print
	while True and not ks:
		s=raw_input('Continue (yes/no)? ')
		if s=='yes':
			break
		elif s=='no':
			sys.exit(1)
	return username, password, hosts, para

def print_host(host,s):
	print '[%s] %s'%(host,s)

def async_out(host,sout):
	def print_out():
		for line in sout:
			print '[%s] %s'%(host,line.strip())
	t=Thread(target=print_out)
	t.start()
	return t

def async_err(host,serr):
	def print_err():
		for line in serr:
			print '[%s ERROR] %s'%(host,line.strip())
	t=Thread(target=print_err)
	t.start()
	return t

def run_concur(fun,hosts):
	threads=[]
	for host in hosts:
		t=Thread(target=fun,args=(host,))
		t.start()
		threads.append(t)
	for t in threads:
		t.join()