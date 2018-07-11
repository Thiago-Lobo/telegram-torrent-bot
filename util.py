#!/usr/bin/python

import logging
import jsonpickle
import json
import random
import datetime

logger = logging.getLogger(__name__)

def object_to_json(object):
	result = {}
	json_object = json.loads(jsonpickle.encode(object))
	
	# logger.debug('this\n%s', json.dumps(json_object, indent=2))

	fields = json_object["_fields"]

	for field in fields:
		result[field] = json_object["_fields"][field]["py/newargs"]["py/tuple"][0]

	logger.debug('Successfully populated JSON with %i fields from object', len(result.keys()))
	# logger.debug('Populated JSON: %s', json.dumps(result))

	return result

def get_named_capture_group(regex, line):
	return re.search(regex, line).groupdict()

def shell_command(command):
	return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

def string_to_timestamp(string):
	return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

def timestamp_to_string(timestamp):
	return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def random_bool():
	return bool(random.getrandbits(1))

def add_seconds_to_timestamp(timestamp, seconds):
	return timestamp + datetime.timedelta(seconds=seconds)

def epoch_to_timestamp(epoch):
	return datetime.datetime.fromtimestamp(epoch)
