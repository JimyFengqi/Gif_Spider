# Gif_Spider

获取GIF资源文件
说明以及具体操作流程日后补上

https://blog.csdn.net/qiqiyingse/article/details/78501034

经常逛A站和B站的人，肯定对一个节目不陌生《网络上常见的GIF动态图》

今天就来分享一下，怎么通过爬虫自动的将这些个动作收藏到自己的电脑中（其实这个程序5月份就写好了，一直拖到现在才想起来将它分享出来）。

一.思路分析
按照爬虫的基本规律：
1.找到目标
2.抓取目标
3.处理目标内容，获取有用的信息

.首先我们的目标是：http://gifcc.com/forum.php    即找动图就上 GIFFCC.COM


这个网站呢，是一个论坛式网站，里面分了几大类，反正试试各种动图。
我们的目标呢，就是找到这（收）些（藏）动（到）图（自）的（己）地（电）址（脑）.

2.看一下各个模块的网址，看一下有什么规律

'http://gifcc.com/forum-37-1.html',#其他各种GIF动态图出处 
'http://gifcc.com/forum-38-1.html', #美女GIF动态图出处 
'http://gifcc.com/forum-47-1.html',#科幻奇幻电影GIF动态图出处
'http://gifcc.com/forum-48-1.html',#喜剧搞笑电影GIF动态图出处
'http://gifcc.com/forum-49-1.html',#动作冒险电影GIF动态图出处
'http://gifcc.com/forum-50-1.html'#恐怖惊悚电影GIF动态图出处
对的，没错，如果以游客身份访问，那么各个板块的网址就是这样的形式 http://gifcc.com/forum-XX -1.html
那么每个模块中的内容又有什么规律？ 来直接上图：



我们关注的是当前页的网址，以及这个页码数，跳到第二页之后，地址变成：http://gifcc.com/forum-38-2.html
那么也就是说 网址的 规律就是 http://gifcc.com/forum-XX-XX.html
这里注意一点，网站的图片是动态加载的， 只有你往下滑动的时候，下面的图片才会逐渐的显现出来,这个暂且记下


3.每一张动图的所在页面的规律


其实这个没啥规律，但是只要我们找到单个图片的地址，就没啥难处理的了.
二 开工动手

1.获取入口页面内容
即根据传入的URL,获取整个页面的源码
[python] view plain copy
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
这里我们使用了webdriver以及PhantomJS 这些模块，为什么呢？因为网页是动态加载的,这样可以抓取的数据全一点.
那这里还有个疑问， 为什么没有滑动啊什么的，得到的数据

2.获取页码数
[python] view plain copy
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
这里的页码处理用到了一个模块pq, 即  PyQuery  
 from pyquery import PyQuery as pq 
采用PyQuery的方式查找我们需要的元素，感觉更好处理一点，挺方便的
同时这里的处理稍微有点意思，如果观察这个页面的话，会发现，每个模块的页码数，在上面和下面都有一个，然后我这里裁取的一下，因为我们只需要一个页码数字即可



3-6 第三步到第六步一起来说
其实就是根据页码数，来进行遍历，获取到每一页的内容
然后得到每一页中的所有图片地址

[python] view plain copy
print  u'总共有 %d页内容' % int(page_num)  
#3.遍历每一页的内容  
for num in range(1,int(page_num)):  
    #4.组装新的url  
    new_url = self.url.replace( self.url.split('-')[2],(str(num)+'.html') )  
    print u'即将获取的页面是：',new_url  
    #5.加载每一页内容，获取gif list 的内容  
    items=self.parse_items_by_html(self.get_all_page(new_url))  
    print u'在第%d页，找到了%d 个图片内容' % (num,len(items))  
    #6.处理每一个元素的内容  
    self.get_items_url(items,num)  
在进行获取每一页的内容的时候，需要重新组装页面地址。
[python] view plain copy
#4.组装新的url  
                new_url = self.url.replace( self.url.split('-')[2],(str(num)+'.html') )  
                print u'即将获取的页面是：',new_url  
有了新的地址，就可以获取当前页面的内容，并进行数据处理，得到每一张图片的地址列表

[python] view plain copy
#5.加载每一页内容，获取gif list 的内容  
                items=self.parse_items_by_html(self.get_all_page(new_url))  
                print u'在第%d页，找到了%d 个图片内容' % (num,len(items))  
[python] view plain copy
#解析页面内容，获取gif的图片list  
def parse_items_by_html(self, html):    
    doc = pq(html)    
    print u'开始查找内容msg'       
    return doc('div[class="c cl"]')  
在获取到图片列表后，再次解析，获取每一张图片的URL
[python] view plain copy
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
在这里，把数据整合一下，为将数据写入数据库做准备
7.将图片存到本地，以及将数据写入数据库

[python] view plain copy
#使用urllib2来获取图片最终地址  
    def get_final_gif_url_use_urllib2(self,url):  
        try:  
            html= urllib2.urlopen(url).read()  
            gif_pattern=re.compile('<div align="center.*?<img id=.*?src="(.*?)" border.*?>',re.S)  
            return re.search(gif_pattern,html).group(1)  
        except Exception,e:  
            print u'获取页面内容出错：',e  
    #最终处理   存贮数据  
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
到这里其实大体的内容已经完成了.
我们能够将这个论坛各个模块的动图都存到本地，同时呢，也将数据放入到了数据库中

三 数据库的筛选
在完成了将数据放入到数据库的之后， 我想着可以直接通过调用数据库，将图片保存
（为什么有这个想法呢，因为我发现如果直接在主程序中存贮图片，它跑的太慢了，不如将数据都放到数据库中，之后专门调用数据库来贮存图片）
但是这里发现一个问题，数据中的内容挺多的，然后发现了好多内容是重复的，因此我们需要对数据库进行去重
关于数据去重的内容，其实我之前的文章已经写过了（写那篇文章的时候，这个爬虫已经完成了呢～）
主要思路是针对某一个元素的数量进行操作，pymongo里面有一个方法是可以统计指定元素的数量的，如果当前元素只有一个，就不管，不是一个元素，就删除
核心代码如下：

[python] view plain copy
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
四 读取数据库中的内容，存贮图片
数据去重之后，再次进行图片的存贮，就方便多了
之后如果图片删除了，也不用重新跑一边，或者说有时候本地图片占地方，那么只用保存有数据库的数据就好了
核心代码如下：


[python] view plain copy
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

完整代码
