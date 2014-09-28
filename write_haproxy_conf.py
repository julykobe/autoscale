#!/usr/bin/env python

import MySQLdb, MySQLdb.cursors

import os

DBHOST = '10.10.82.112'
DBUSER = 'root'
DBPASSWORD = '123456'
DB = 'InSTech_GAI'
group_id = 20

conf_path = '/usr/local/haproxy/haproxy.conf'

def read_private_ip(group_id):
	con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
	cursor = con.cursor()
	sql = "select ip from instances where group_id =" + str(group_id)
	cursor.execute(sql)
	inst_ip = cursor.fetchall()
	'''
	>>> inst_ip
	(('192.168.11.11',), (None,))
	'''
	cursor.close()
	con.close()

	#return a list
	return inst_ip

def read_public_ip(group_id):	
	con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
	cursor = con.cursor()
	sql = "select publicDNS from EC2Instance where group_id =" + str(group_id)
	cursor.execute(sql)
	inst_ip = cursor.fetchall()
	cursor.close()
	con.close()
	'''
	>>> inst_ip
	(('[54.64.175.229]',),)
	>>> inst_ip[0]
	('[54.64.175.229]',)
	>>> inst_ip[0][0]
	'[54.64.175.229]'
	>>> inst_ip[0][0][1:-1]
	'54.64.175.229'
	'''
	return inst_ip

def format_list(unformat_list, source = 'private'):
	#format:
	#private:server page1 10.10.89.111:80 weight 3 check inter 1500 rise 3 fall 3
	#public:server page1 10.10.89.111:80 weight 1 check inter 1500 rise 3 fall 3

	#format to a ip list
	if source == 'private':
		inst_ip = map(lambda x:x[1],unformat_list)
		weight = 1
	elif source == 'public':
		inst_ip = map(lambda x:x[0][1:-1],unformat_list)
		weight = 3

	#finally format to a list of lines
	format_lines = map(lambda ip:'\tserver %s %s:80 weight %d check inter 1500 rise 3 fall 3\n' % (ip,ip,weight),inst_ip)
	
	#return
	return format_lines

if __name__ == '__main__':
	#read private instances ip from db
	private_list = read_private_ip(group_id)

	#format the list
	format_private = format_list(private_list, source = 'private')

	#read public instances ip from db
	public_list = read_public_ip(group_id)

	format_public = format_list(public_list, source = 'public')

	#construct a list
	format_list = format_private + format_public

	#open the conf file
	fd = open(conf_path,'a')

	#write conf
	map(lambda x:fd.writelines(x),format_list)

	#close conf
	fd.close()

	#restart 
	#os.system("killall haproxy")
	#os.system("/usr/local/haproxy/sbin/haproxy -f /usr/local/haproxy/haproxy.conf")
