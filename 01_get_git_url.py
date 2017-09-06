#coding: utf-8 
from pyquery import PyQuery as pq  
from selenium import webdriver 
import HTMLParser,urllib2,urllib,re,os

import pymongo

import time
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')  
class download_gif:
	def __init__(self):
		self.url='http://gifcc.com/forum-38-1.html'
		self.url_list=['http://gifcc.com/forum-37-1.html',#其他各种GIF动态图出处 
		'http://gifcc.com/forum-38-1.html', #美女GIF动态图出处 
		'http://gifcc.com/forum-47-1.html',#科幻奇幻电影GIF动态图出处
		'http://gifcc.com/forum-48-1.html',#喜剧搞笑电影GIF动态图出处
		'http://gifcc.com/forum-49-1.html',#动作冒险电影GIF动态图出处
		'http://gifcc.com/forum-50-1.html'#恐怖惊悚电影GIF动态图出处
		]
		self.choices={'1':u'其他各种GIF动态图出处',
		'2':u'美女GIF动态图出处',
		'3':u'科幻奇幻电影GIF动态图出处',
		'4':u'喜剧搞笑电影GIF动态图出处',
		'5':u'动作冒险电影GIF动态图出处',
		'6':u'恐怖惊悚电影GIF动态图出处'
		}
		
		self.dir_name=u'gif出处'
		self.gif_list=[]
		
		self.connection = pymongo.MongoClient()  
		
		#BookTable.insert_one(dict_data)#插入单条数据  
		#BookTable.insert(dict_data)#插入 字典list 数据 
		
	#获取页面内容，并且加载JS, 通过滚动获取页面更多的元素
	def get_all_page(self,url):
		try:
			#browser = webdriver.PhantomJS(executable_path=r'C:\Python27\Scripts\phantomjs.exe') 
			browser = webdriver.PhantomJS() 
			browser.get(url)
			#time.sleep(3) 
			#页面滚动
			js = "var q=document.body.scrollTop=100000"    
			#for i in range(5):  #调试语句，先暂时不加载太多次数
			for i in range(30):  
				#循环执行下滑页面50次  
				browser.execute_script(js)  
				#加载一次，休息一下  
				time.sleep(1)
				print u'这是第 %d 次划动页面' % i
			# 执行js得到整个页面内容
			html = browser.execute_script("return document.documentElement.outerHTML")
			browser.close()
			html=HTMLParser.HTMLParser().unescape(html)
			return html
		except Exception,e:
			print u'发生错误：',e
	
	#解析页面内容，获取gif的图片list
	def parse_items_by_html(self, html):  
		doc = pq(html)  
		print u'开始查找内容msg'     
		return doc('div[class="c cl"]')
		
	#解析gif 的list ，处理每一个gif内容
	def get_items_url(self,items,num):
		i=1
		for article in items.items():
			print u'开始处理数据(%d/%d)' % (i, len(items))
			#print article
			self.get_single_item(article,i,num)
			i +=1
	
	#处理单个gif内容，获取其地址，gif 最终地址
	def get_single_item(self,article,num,page_num):
		gif_dict={}
		#每个页面的地址
		gif_url= 'http://gifcc.com/'+article('a').attr('href')
		#每个页面的标题
		gif_title= article('a').attr('title')
		
		#每张图的具体地址
		#html=self.get_html_Pages(gif_url)
		#gif_final_url=self.get_final_gif_url(html)
	 
		gif_dict['num']=num
		gif_dict['page_num']=page_num
		gif_dict['gif_url']=gif_url
		gif_dict['gif_title']=gif_title
		self.gif_list.append(gif_dict)
		data=u'第'+str(page_num)+'页|\t'+str(num)+'|\t'+gif_title+'|\t'+gif_url+'\n'
		self.file_flag.write(data)
	
	#通过webdriver获得页面内容后，获得最终地址
	def get_final_gif_url(self,html):
		doc = pq(html) 
		image_content= doc('td[class="t_f"]')
		gif_url= image_content('img').attr('src')
		return gif_url
	
	#使用urllib2来获取图片最终地址
	def get_final_gif_url_use_urllib2(self,url):
		try:
			html= urllib2.urlopen(url).read()
			gif_pattern=re.compile('<div align="center.*?<img id=.*?src="(.*?)" border.*?>',re.S)
			return re.search(gif_pattern,html).group(1)
		except Exception,e:
			print u'获取页面内容出错：',e
	#最终处理	存贮数据
	def get_gif_url_and_save_gif(self):
		def save_gif(url,name):
			try:
				urllib.urlretrieve(url, name)
			except Exception,e:
				print '存贮失败，原因：',e
		for i in range(0,len(self.gif_list)):
			gif_dict=self.gif_list[i]
			gif_url=gif_dict['gif_url']
			gif_title=gif_dict['gif_title']
			
			#依然使用webdriver获取最终的gif地址
			final_html=self.get_html_Pages(gif_url)
			gif_final_url=self.get_final_gif_url(final_html)
			#使用另外一种方式（urllib2）获取最终地址
			#gif_final_url=self.get_final_gif_url_use_urllib2(gif_url)
			
			gif_dict['gif_final_url']=gif_final_url
			print u'开始向数据库写入第%d页第%d项数据，并开始存贮图片到本地 ' % (gif_dict['page_num'],gif_dict['num'])
			self.BookTable.insert_one(gif_dict)
			gif_name=self.dir_name+'/'+gif_title+'.gif'
			save_gif(gif_final_url,gif_name)
		
	#仅仅获取页面内容
	def get_html_Pages(self,url):  
		try:   
			#browser = webdriver.PhantomJS(executable_path=r'C:\Python27\Scripts\phantomjs.exe') 
			browser = webdriver.PhantomJS() 
			browser.get(url)
			html = browser.execute_script("return document.documentElement.outerHTML")
			browser.close()
			html=HTMLParser.HTMLParser().unescape(html).decode('utf-8')
			return html
        #捕捉异常，防止程序直接死掉    
		except Exception,e:  
			print u"连接失败，错误原因",e
			return None   
	
	#获取页码		
	def get_page_num(self,html):

		doc = pq(html)  
		print u'开始获取总页码'
		#print doc('head')('title').text()#获取当前title
		try:
			#如果当前页面太多，超过8页以上，就使用另一种方式获取页码
			if doc('div[class="pg"]')('[class="last"]'):
				num_content= doc('div[class="pg"]')('[class="last"]').attr('href')
				print  num_content.split('-')[1].split('.')[0]
				return num_content.split('-')[1].split('.')[0]
			else:
				num_content= doc('div[class="pg"]')('span')
				return filter(str.isdigit,str(num_content.text()))[0]
		#如果获取页码失败，那么就返回1， 即值获取1页内容	
		except Exception,e:
			print u'获取页码失败'.e
			return '1'
			
		# filter(str.isdigit,num_content)#从字符串中提取数字
		
	#创建文件夹	
	def mk_dir(self,path):
		if not os.path.exists(path):  
			os.makedirs(path) 
			
	def set_db(self,tablename):
		self.BookDB = self.connection.GifDB         #数据库db的名字  
		self.BookTable =self.BookDB[tablename]           #数据库table表的名字  
			
	#主函数		
	def run(self):
		choice_type=5
		if choice_type:
		#for choice_type in range(len(self.choices)): 
			if  choice_type+1:
				
				self.dir_name=self.choices[str(choice_type+1)].strip()
				self.url=self.url_list[int(choice_type)]
				
				
				print self.dir_name,self.url
		
		
			#0.创建文件夹存贮图片,建立文件存贮内容
			self.mk_dir(self.dir_name)
			self.filename=self.dir_name+'/'+self.dir_name+'.txt'
			print self.filename
			self.file_flag=open(self.filename,'w')
			
			self.set_db(self.dir_name)
			self.BookTable .insert({'filename':self.dir_name})
			
			print self.url
			#1.获取入口页面内容
			html=self.get_html_Pages(self.url)
			
			#2.获取页码数目
			page_num=self.get_page_num(html)
			
			print  u'总共有 %d页内容' % int(page_num)
			#3.遍历每一页的内容
			
			#page_num=3#调试语句，先暂时将页面内容设置的小一点
			for num in range(1,int(page_num)):
				#4.组装新的url
				new_url = self.url.replace( self.url.split('-')[2],(str(num)+'.html') )
				print u'即将获取的页面是：',new_url
				#5.加载每一页内容，获取gif list 的内容
				items=self.parse_items_by_html(self.get_all_page(new_url))
				print u'在第%d页，找到了%d 个图片内容' % (num,len(items))
				#6.处理每一个元素的内容
				self.get_items_url(items,num)
			
			#5.数据全部抓取完毕，开始处理数据
			self.get_gif_url_and_save_gif()
			print 'success'
			
			self.file_flag.close()
		
			
if __name__ == '__main__':  
	print u'''
            **************************************************  
            **    Welcome to Spider of  GIF 出处图片        **  
            **         Created on 2017-05-21                **  
            **         @author: Jimy _Fengqi                **  
            ************************************************** 
	'''  		
	print u''' 选择你要下载的gif图片类型
		1:'其他各种GIF动态图出处'
		2:'美女GIF动态图出处'
		3:'科幻奇幻电影GIF动态图出处'
		4:'喜剧搞笑电影GIF动态图出处'
		5:'动作冒险电影GIF动态图出处'
		6:'恐怖惊悚电影GIF动态图出处'
		'''
	#选择要下载的类型	

	mydownload=download_gif()
	html=mydownload.run()
	
		
		
