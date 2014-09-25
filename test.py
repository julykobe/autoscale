#!/usr/bin/env python
import time
import rule

if __name__ == "__main__":
	while True:
		import pdb
		pdb.set_trace()
		rule.check_all_rules()
		fd = open('/tmp/my_daemon_log.dat', 'a')
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		fd.write(str(now)+'\n')
		fd.close()
