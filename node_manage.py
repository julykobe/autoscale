#author: Ryan Huang
#desc: InSTech_Cloud Node Management
#-----------------------------
#2014-12-21 created
#2014-12-22 modified
#-----------------------------

import os,sys
import dbHelper

class computeNode(object):
    def __init__(self,host,user='root',description=''):
        self.hostname=host
        if self.isExist():
            nodeInfo=dbHelper.nodeDetails(self.hostname)
            self.ipAddress=nodeInfo['ip']
            self.sysUser=nodeInfo['user']
            self.macAddress=nodeInfo['mac']
            self.state=nodeInfo['state']
        else:
            self.sysUser=user
            self.description=description
            self.ipAddress=''
            self.macAddress=''
            self.state='down'
    
    def isExist(self):
        return  dbHelper.isNodeExist(self.hostname)  
     
#node start
    def start(self):
        try:
            if self.state=='up':
                return True
            else:
		os.system(("sudo wakeonlan '%s'")%(self.macAddress))
                self.state='up'
                dbHelper.nodeUpdateState(self.hostname,self.state)
                return True
        except:
            return False  

#node stop
    def stop(self):
        try:
            if self.state=='down':
                return True
            else:
                os.popen(("sudo ssh '%s'@'%s' service nova-compute stop")%(self.sysUser, self.hostname))
          	os.system(("sudo ssh '%s'@'%s' init 0")%(self.sysUser, self.hostname))
                self.state='down'
                dbHelper.nodeUpdateState(self.hostname,self.state)
                return True
        except:
            return False

#add node
#del node

