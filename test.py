#!/usr/bin/env python


import log

import time
import rule
import utils

LOG = log.get_logger()

if __name__ == "__main__":
	while True:
		mode = utils.get_config('mode', 'testing')
		if 'True' == mode:
			LOG.warning("NOW running in testing mode")
		rule.check_all_rules()
		LOG.info("All rules have been checked")