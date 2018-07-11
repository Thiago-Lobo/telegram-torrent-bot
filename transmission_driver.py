#!/usr/bin/python

import sys
import os
import re
import json
import subprocess
import time
import transmissionrpc
import logging
import util
import traceback
from datetime import datetime, timedelta
from optparse import OptionParser

PREALLOCATION_TIMEOUT_THRESHOLD = 6.0
TRANSMISSION_DAEMON_HOSTNAME = 'localhost'
TRANSMISSION_DAEMON_PORT = 9091
ALL_TORRENTS_STRING = 'all'
DOWNLOADS_PATH = '/mnt/the_vault'

logger = logging.getLogger(__name__)
rpc = None

status_mapping = {
    0: 'stopped',
    1: 'check pending',
    2: 'checking',
    3: 'download pending',
    4: 'downloading',
    5: 'seed pending',
    6: 'seeding',
}

class PreallocationException(Exception):
	pass

def initialize():
	global rpc
	logger.info('Initializing Transmission Daemon Driver module at [%s:%s]', TRANSMISSION_DAEMON_HOSTNAME, TRANSMISSION_DAEMON_PORT)
	rpc = transmissionrpc.Client(address=TRANSMISSION_DAEMON_HOSTNAME, port=TRANSMISSION_DAEMON_PORT)
	logger.debug('Initialized session information:\n%s', json.dumps(util.object_to_json(rpc.get_session())))
	logger.debug('RPC timeout: %s', rpc.timeout)

def get_torrent_status(status_id):
	if status_id > 6 or status_id < 0:
		return "invalid"

	return status_mapping[status_id]

def get_status_id(status_name):
	for key, value in status_mapping.iteritems():
		if value == status_name:
			return key

	return -1

def check_preallocation():
	try:
		logger.debug('PREALLOCATION_TIMEOUT_THRESHOLD is set to %.1f s. Will try to communicate with transmission daemon.', PREALLOCATION_TIMEOUT_THRESHOLD)
		rpc.get_session(timeout=PREALLOCATION_TIMEOUT_THRESHOLD)
	except Exception as ex:
		logger.exception('Exception caught')
		if type(ex).__name__ == 'timeout':
			logger.debug('Exception type is timeout. Will raise PreallocationException.')
			raise PreallocationException('Transmission daemon is preallocating. Try again later.')
		pass

def torrent_hash_to_id(hashes):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.debug('Converting hash vector: %s to id vector', json.dumps(hashes))

	result = ALL_TORRENTS_STRING

	if hashes != ALL_TORRENTS_STRING:
		if not isinstance(hashes, list):
			hashes = [ hashes ]
		result = [x.id for x in rpc.get_torrents() if x.hashString in hashes]

	logger.debug('Converted id vector: %s', json.dumps(result))

	return result

def get_all_torrent_ids():
	return [x.id for x in rpc.get_torrents()]

def handle_ids_argument(ids):
	logger.debug('Handling ids argument: %s', json.dumps(ids))

	if ids == ALL_TORRENTS_STRING:
		ids = get_all_torrent_ids()

	return ids

def get_torrent_info_by_id(ids):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	ids = handle_ids_argument(ids)

	logger.info('Will attempt to get information for torrents with ids: %s', json.dumps(ids))

	return [util.object_to_json(x) for x in rpc.get_torrents(ids)]

def get_torrent_info_by_hash(hashes):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to get information for torrents with hashes: %s', json.dumps(hashes))
	ids = torrent_hash_to_id(hashes)

	return get_torrent_info_by_id(ids)

def add_torrent_magnet_link(magnet_link):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Got magnet_link: "%s"', magnet_link)
	added_torrent = rpc.add_torrent(magnet_link)
	json_torrent_data = util.object_to_json(added_torrent)
	logger.debug('Added torrent data:\n%s', json.dumps(json_torrent_data))
	return json_torrent_data

def pause_torrent_by_id(ids):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	ids = handle_ids_argument(ids)

	logger.info('Will attempt to pause torrents with ids: %s', json.dumps(ids))
	rpc.stop_torrent(ids)

def pause_torrent_by_hash(hashes):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to pause torrents with hashes: %s', json.dumps(hashes))
	ids = torrent_hash_to_id(hashes)

	return pause_torrent_by_id(ids)

def resume_torrent_by_id(ids):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	ids = handle_ids_argument(ids)

	logger.info('Will attempt to resume torrents with ids: %s', json.dumps(ids))
	rpc.start_torrent(ids)

def resume_torrent_by_hash(hashes):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to resume torrents with hashes: %s', json.dumps(hashes))
	ids = torrent_hash_to_id(hashes)

	return resume_torrent_by_id(ids)

def remove_torrent_by_id(ids):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	ids = handle_ids_argument(ids)

	logger.info('Will attempt to remove torrents with ids: %s', json.dumps(ids))
	rpc.remove_torrent(ids, delete_data = True)

def remove_torrent_by_hash(hashes):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to remove torrents with hashes: %s', json.dumps(hashes))
	ids = torrent_hash_to_id(hashes)

	return remove_torrent_by_id(ids)

def get_free_space():
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to get free space at DOWNLOADS_PATH')
	return rpc.free_space(DOWNLOADS_PATH) / (1024.0 * 1024.0 * 1024.0)

def get_session_info():
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to get session info')
	return util.object_to_json(rpc.get_session())

def get_session_stats():
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to get session stats')
	return util.object_to_json(rpc.session_stats())

def set_session_property(**kwargs):
	try:
		check_preallocation()
	except PreallocationException:
		raise

	logger.info('Will attempt to set session data fields: %s', json.dumps(kwargs))
	rpc.set_session(**kwargs)
