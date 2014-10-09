import umysql
from functools import wraps

import utils

DBHOST = utils.get_config('database', 'DBHOST')
DBUSER = utils.get_config('database', 'DBUSER')
DBPASSWORD = utils.get_config('database', 'DBPASSWORD')
DB = utils.get_config('database', 'DB')

class Configuration:
	def __init__(self, env):
		if "Prod" == env:
			self.host = DBHOST
			self.port = 3306
			self.db = DB
			self.user = DBUSER
			self.passwd = DBPASSWORD
		elif "Test" == env:
			self.host = DBHOST
			self.port = 3306
			self.db = DB
			self.user = DBUSER
			self.passwd = DBPASSWORD

def mysql(sql):
	_conf = Configuration(env="Prod")

	def on_sql_error(err):
		print err
		sys.exit(-1)

	def handle_sql_result(rs):
		if rs.rows > 0:
			fieldnames = [f[0] for f in rs.fields]
			return [dict(zip(fieldnames, r)) for r in rs.rows]
		else:
			return []

	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			mysqlconn = umysql.Connection()
			mysqlconn.settimeout(5)
			mysqlconn.connect(_conf.host, _conf.port, _conf.user, \
								_conf.passwd, _conf.db, True, 'utf8')
			try:
				rs = mysqlconn.query(sql,{})
			except umysql.Error as e:
				on_sql_error(e)

			data = handle_sql_result(rs)
			kwargs["data"] = data
			result = fn(*args, **kwargs)
			mysqlconn.close()
			return result
		return wrapper

	return decorator

@mysql(sql = "select * from autoscale_rules")
def get_rules(data):
	print data

if __name__ == "__main__":
	get_rules()