#coding: utf-8 
from pyquery import PyQuery as pq  
from selenium import webdriver 
import HTMLParser,urllib2,urllib,re,os

import pymongo

import time
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')  

import pymongo  

def save_gif(url,name):
	try:
		urllib.urlretrieve(url, name)
	except Exception,e:
		print u'存贮失败，原因：',e
client = pymongo.MongoClient('localhost', 27017) 
print client.database_names()


db = client.GifDB
for table in  db.collection_names():
	print 'table name is ',table
	collection=db[table]

	for item in  collection.find():
		try: 
			if item['gif_final_url']:
				url,url_title= item['gif_final_url'],item['gif_title']
				gif_filename=table+'/'+url_title+'.gif'
				print 'start save %s, %s' % (url,gif_filename)
				save_gif(url,gif_filename)
		except Exception,e:
			print u'错误原因：',e
			


