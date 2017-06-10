#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-04-27 00:33:51
# Project: lyric2

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):

        list = ['http://music.baidu.com/search?key=%E7%8E%8B%E5%8A%9B%E5%AE%8F','http://music.baidu.com/search/song?s=1&key=%E5%91%A8%E6%9D%B0%E4%BC%A6','http://music.baidu.com/search?key=%E6%BD%98%E7%8E%AE%E6%9F%8F','http://music.baidu.com/search?key=%E6%9E%97%E4%BF%8A%E6%9D%B0']

        for i in list:
            self.crawl(i, callback=self.index_page,fetch_type='js')

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('span.song-title > a').items():
            self.crawl(each.attr.href,fetch_type='js',callback=self.detail_page)
            print("抓了一首歌")
        for each in response.doc('a.page-navigator-next').items():
            self.crawl(each.attr.href,fetch_type='js',callback=self.index_page)



    @config(priority=2)
    def detail_page(self, response):
        a = 'div.song-info > div.info-holder.clearfix > ul > li:nth-child(2) > a'
        if len(response.doc(a).text()) <1:
            a = 'div.song-info > div.info-holder.clearfix > ul > li:nth-child(3) > a'

        if len(response.doc('div.song-info > div.play-holder.clearfix > div > h2').text())>0:
            return {
                "alblum": response.doc(a).text(),
                "titles": response.doc('div.song-info > div.play-holder.clearfix > div > h2').text(),
                "content": response.doc('#lyricCont').text(),
                "author":(response.doc('.author_list').text()).split()[0],
            }

    def index_page2(self, response):
        return "我被执行了"
