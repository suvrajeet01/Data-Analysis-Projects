from pyspider.libs.base_handler import *

class Handler(BaseHandler):



    crawl_config = {
    }
    @every(minutes=24 * 60)
    def on_start(self):
        for i in range(110): #ajust by actual needs
            url = 'http://www.shixiseng.com/interns?k=%E6%95%B0%E6%8D%AE&c=%E5%85%A8%E5%9B%BD&s=0,0&d=&m=&x=&t=zh&ch=&p=' + str(i)
            self.crawl(url,callback=self.list_page)

    @config(age=10*24*60*60)
    def list_page(self,response,num=None):
        for each in response.doc('#load_box_item > div> div > div > a').items():
            self.crawl(each.attr.href,callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "title":response.doc('.job_name').text(),
            "daymoney":response.doc('.daymoney').text(),
            "location":response.doc('.city').text(),
            "days":response.doc('.days').text(),
            "lasting":response.doc('.month').text(),
            "jobdescribe":response.doc('.dec_content').text(),
            "industry":response.doc('.domain > span').text(),
        }
