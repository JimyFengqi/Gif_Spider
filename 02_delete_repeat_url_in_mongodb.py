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
		print '存贮失败，原因：',e
		
def print_database_and_table_name():	
	import pymongo
	client = pymongo.MongoClient('localhost', 27017) 
	print client.database_names()

	for database in client.database_names():
		for table in  client[database].collection_names():
			print 'table  [%s]  is in database [%s]' % (table,database)

def delete_single_database_repeat_data():
	import pymongo
	client = pymongo.MongoClient('localhost', 27017) 
	db=client.GifDBtemptemp2#这里是将要清洗数据的数据库名字
	for table in  db.collection_names():
		print 'table name is ',table
		collection=db[table]
		for url in collection.distinct('gif_title'):#使用distinct方法，获取每一个独特的元素列表
			num= collection.count({"gif_title":url})#统计每一个元素的数量
			print num
			for i in range(1,num):#根据每一个元素的数量进行删除操作，当前元素只有一个就不再删除
				print 'delete %s %d times '% (url,i)
				#注意后面的参数， 很奇怪，在mongo命令行下，它为1时，是删除一个元素，这里却是为0时删除一个
				collection.remove({"gif_title":url},0)
			for i in  collection.find({"gif_title":url}):#打印当前所有元素
				print i

def delete_repeat_data():
	import pymongo
	client = pymongo.MongoClient('localhost', 27017) 
	db = client.local
	collection = db.person
	
	for url in collection.distinct('name'):#使用distinct方法，获取每一个独特的元素列表
		num= collection.count({"name":url})#统计每一个元素的数量
		print num
		for i in range(1,num):#根据每一个元素的数量进行删除操作，当前元素只有一个就不再删除
			print 'delete %s %d times '% (url,i)
			#注意后面的参数， 很奇怪，在mongo命令行下，它为1时，是删除一个元素，这里却是为0时删除一个
			collection.remove({"name":url},0)
		for i in  collection.find({"name":url}):#打印当前所有元素
			print i
	print collection.distinct('name')#再次打印一遍所要去重的元素
delete_single_database_repeat_data()