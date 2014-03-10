#!/usr/bin/python
import os

dd={}
dd['Others']=0
procs=('NameNode','DataNode','JobTracker','TaskTracker','HMaster','HRegionServer','QuorumPeerMain')

def v(s):
	if s in dd:
		return dd[s]
	else:
		return 0

for p in os.popen('jps'):
	s=p.split()
	t=int(os.popen('ps -Lf '+s[0]+' | wc -l').readline()[0:-1])-1
	if s[1]=='Child':
		if 'Child' in dd:
			dd['Tasks']+=1
			dd['Child']+=t
		else:
			dd['Tasks']=1
			dd['Child']=t
	elif s[1] in procs:
		dd[s[1]]=t-1
	else:
		dd['Others']+=t
print '  NameNode  DataNode  JobTracker  TaskTracker  TaskAttempts  HMaster  HRegionServer  ZooKeeper  Others'
ta='%d/%d'%(v('Tasks'),v('Child'))
r='%10d%10d%12d%13d'%(v('NameNode'),v('DataNode'),v('JobTracker'),v('TaskTracker'))
r+='%14s%9d%15d%11d%8d'%(ta,v('HMaster'),v('HRegionServer'),v('QuorumPeerMain'),dd['Others'])
print r