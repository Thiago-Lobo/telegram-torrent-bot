#!/usr/bin/python

import logging
import sqlite3

DATABASE_PATH = 'data.db'

QUERY_CREATE_TBL_TORRENT_RECORD = '''
	create table if not exists TBL_TORRENT_RECORD
	(
		TTR_ID INTEGER PRIMARY KEY AUTOINCREMENT,
		TTR_HASHSTRING TEXT,
		TTR_REPORTED INTEGER
	) 
'''

QUERY_CREATE_TBL_TORRENT_USER = '''
	create table if not exists TBL_TORRENT_USER
	(
		TTU_ID INTEGER PRIMARY KEY AUTOINCREMENT,
		TTR_ID INTEGER,
		TTU_USERNAME TEXT
	) 
'''

QUERY_INSERT_TBL_TORRENT_RECORD = '''
	insert into TBL_TORRENT_RECORD (TTR_HASHSTRING, TTR_REPORTED) values (?,?)
'''

QUERY_INSERT_TBL_TORRENT_USER = '''
	insert into TBL_TORRENT_USER (TTR_ID, TTU_USERNAME) values (?,?)
'''

QUERY_SET_TORRENT_REPORTED = '''
	update 
		TBL_TORRENT_RECORD
	set
		TTR_REPORTED = 1
	where
		TTR_HASHSTRING = (?)
'''

QUERY_SELECT_TORRENTS_HASHSTRINGS_BY_USERNAME = '''
	select 
		TTR_HASHSTRING 
	from 
		TBL_TORRENT_USER u, 
		TBL_TORRENT_RECORD t 
	where 
		t.TTR_ID = u.TTR_ID 
	and 
		u.TTU_USERNAME = (?)
'''

QUERY_SELECT_USERS_BY_TTR_HASHSTRING = '''
	select 
		TTU_USERNAME 
	from 
		TBL_TORRENT_USER u, 
		TBL_TORRENT_RECORD t 
	where 
		t.TTR_ID = u.TTR_ID 
	and 
		t.TTR_HASHSTRING = (?)
'''

QUERY_SELECT_UNREPORTED_TORRENT_HASHSTRINGS = '''
	select 
		TTR_HASHSTRING 
	from 
		TBL_TORRENT_RECORD
	where 
		TTR_REPORTED = 0
'''

logger = logging.getLogger(__name__)

def get_db():
	db = sqlite3.connect(DATABASE_PATH)
	db.row_factory = sqlite3.Row
	return db

def create_tables():
	db = get_db()
	cursor = db.cursor()
	cursor.execute(QUERY_CREATE_TBL_TORRENT_RECORD)
	cursor.execute(QUERY_CREATE_TBL_TORRENT_USER)
	db.commit()

def initialize():
	logger.info('Initializing SQLite3 Module at [%s]', DATABASE_PATH)
	create_tables()

def insert_torrent_record(hash_string):
	db = get_db()
	cursor = db.cursor()
	logger.info('Inserting torrent record with hash_string [%s]', hash_string)
	cursor.execute(QUERY_INSERT_TBL_TORRENT_RECORD, (hash_string, 0))
	db.commit()

	return cursor.lastrowid

def insert_torrent_user(ttr_id, username):
	db = get_db()
	cursor = db.cursor()
	logger.info('Inserting torrent [%s] user with username [%s]', ttr_id, username)
	cursor.execute(QUERY_INSERT_TBL_TORRENT_USER, (ttr_id, username))
	db.commit()

	return cursor.lastrowid

def get_torrent_hashes_by_user(username):
	db = get_db()
	cursor = db.cursor()
	logger.info('Querying for torrents linked to username [%s]', username)
	cursor.execute(QUERY_SELECT_TORRENTS_HASHSTRINGS_BY_USERNAME, (username,))
	
	return [x['TTR_HASHSTRING'] for x in cursor]

def get_users_by_torrent_hash(hash_string):
	db = get_db()
	cursor = db.cursor()
	logger.info('Querying for usernames linked to torrent record with hash [%s]', hash_string)
	cursor.execute(QUERY_SELECT_USERS_BY_TTR_HASHSTRING, (hash_string,))
	
	return [x['TTU_USERNAME'] for x in cursor]

def get_unreported_torrents_hashstrings():
	db = get_db()
	cursor = db.cursor()
	logger.info('Querying for unreported torrents\' hashes')
	cursor.execute(QUERY_SELECT_UNREPORTED_TORRENT_HASHSTRINGS)
	
	return [x['TTR_HASHSTRING'] for x in cursor]

def set_torrent_reported(hash_string):
	db = get_db()
	cursor = db.cursor()
	logger.info('Flagging torrent record [%s] as reported', hash_string)
	cursor.execute(QUERY_SET_TORRENT_REPORTED, (hash_string,))
	db.commit()

def main():
	initialize()

	row_id = insert_torrent_record('a')
	insert_torrent_user(row_id, 'thiago')
	insert_torrent_user(row_id, 'leila')

	row_id = insert_torrent_record('b')
	insert_torrent_user(row_id, 'daniela')

	db = get_db()
	cursor = db.cursor()
	cursor.execute('''select * from TBL_TORRENT_RECORD''')
	for row in cursor:
		print row

	# print get_users_by_torrent_hash('cfa0ac1529ba6eb4279c18334b380781dd74f86d')
	# print get_users_by_torrent_hash('b')
	# set_torrent_reported('a')

	# cursor.execute('''select * from TBL_TORRENT_RECORD''')
	# for row in cursor:
	# 	print row

if __name__ == '__main__':
	main()
