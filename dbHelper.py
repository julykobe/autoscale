#!/usr/bin/python
#-*-coding:utf-8-*-
#author: Ryan Huang
#desc: interface to operate db
#-----------------------------
#2014-12-21 created 

#-----------------------------

import sys,time
import MySQLdb, dbConf
#from mysql.connector import errorcode

def getConnectionForDB():
	chost=dbConf.DBHOST
	cport=dbConf.DBPORT
	cuser=dbConf.DBUSER
	cpassword=dbConf.DBPASSWORD
	cdbname=dbConf.DBNAME
	try:
		cnx=MySQLdb.connect(user=cuser,passwd=cpassword,host=chost,db=cdbname)
		return cnx
	except:
  		sys.exit(1)
def isNodeExist(nodeName):
        try:
		cnx=getConnectionForDB()
		cursor = cnx.cursor()
		query=("select count(*) from hardware where hardwareName = '%s';")%(nodeName)		
		cursor.execute(query)
		if cursor.fetchone()[0]==1:
                        return True
        except:
		cnx.rollback()
	cursor.close()
	cnx.close()
        return False

def nodeDetails(nodeName):
        nodeInfo={}
        try:
                cnx=getConnectionForDB()
		cursor = cnx.cursor()
		query=("select hardwareIp,sysUser,MAC,state from hardware where hardwareName ='%s';")%(nodeName)
		cursor.execute(query)
		details=cursor.fetchone()
		nodeInfo['ip']=details[0]
		nodeInfo['user']=details[1]
		nodeInfo['mac']=details[2]
		nodeInfo['state']=details[3]
		cnx.commit()
	except:
		cnx.rollback()
	cursor.close()
	cnx.close()
	return nodeInfo

def nodeUpdateState(nodeName,state):
        #ctime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
	try:
		cnx=getConnectionForDB()
		cursor = cnx.cursor()
		updateTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
		query=("update hardware set state='%s',updated_at='%s' where hardwareName='%s';")%(state,updateTime,nodeName)
		cursor.execute(query)
                cnx.commit()
	except:
		cnx.rollback()
	cursor.close()
	cnx.close()

