#!/usr/bin/env python
from __future__ import with_statement
import ConfigParser
import logging

import time
import rule
import utils

if __name__ == "__main__":

	logging.basicConfig(level = logging.DEBUG,
					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
					datefmt = '%a, %d %b %Y %H:%M:%S',
					filename = 'autoscaling.log',
					filemode = 'w')

	mode = utils.get_config('mode', 'testing')
	logging.warning(mode)
	'''
	while True:
		import pdb
		pdb.set_trace()
		rule.check_all_rules()
		fd = open('/tmp/my_daemon_log.dat', 'a')
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		fd.write(str(now)+'\n')
		fd.close()
	'''
