import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict

class CnThepaperSpider(CrawlSpider):

    name = "cn.thepaper"
    redis_key = "cn.thepaper"

    def start_requests(self):
        self.headers = {}
        self.headers['authority'] = 'm.thepaper.cn'
        self.headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        self.headers['accept-language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        self.headers['cache-control'] = 'max-age=0'
        self.headers['cookie'] = 'Hm_lvt_94a1e06bbce219d29285cee2e37d1d26=1685066120,1687322509; Hm_lvt_d07e4d64d5cde19b5351e7032beaef1a=1696753160; acw_tc=76b20f7316967531682828055e0afc44894e88f21a63f0d13646b7a25315e0; route=d78c33638bbf64f41c252dfa8b47408d; Hm_lpvt_d07e4d64d5cde19b5351e7032beaef1a=1696753286'
        self.headers['sec-ch-ua'] = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers['sec-ch-ua-mobile'] = '?0'
        self.headers['sec-ch-ua-platform'] = '"Windows"'
        self.headers['sec-fetch-dest'] = 'document'
        self.headers['sec-fetch-mode'] = 'navigate'
        self.headers['sec-fetch-site'] = 'none'
        self.headers['sec-fetch-user'] = '?1'
        self.headers['upgrade-insecure-requests'] = '1'
        self.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'

        self.encoding = "utf-8"

        url = 'https://m.thepaper.cn/'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = 'https://m.thepaper.cn/channel_143064'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = 'https://m.thepaper.cn/channel_25950'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = 'https://m.thepaper.cn/channel_122908'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = 'https://m.thepaper.cn/channel_25951'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = 'https://m.thepaper.cn/channel_119908'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//div[starts-with(@class, 'index_contentBox')]/a[starts-with(@class, 'index_inherit')]"
        links = extractor.list_link_anchor(dom, x, response.request.url)
        if links:
            for href, anchor in links:
                self.logger.info(f"outlinks: {href}, {anchor}")
                meta = response.request.meta
                meta['anchor'] = anchor
                meta['outlink'] = href
                yield Request(url=href, callback=self.parse_detail, headers=self.headers, meta=meta)

    def parse_detail(self, response):

        #html = response.body.decode(self.encoding)
        #dom = etree.HTML(html)
        #x = '//h1//text()'
        #title = extractor.get_text(dom, x)
        #self.logger.info(f"parse_detail: title: {title}")

        #x = "//div[starts-with(@class, 'index_left')]/div/text()"
        #author = extractor.get_text(dom, x)
        #self.logger.info(f"parse_detail: author: {author}")

        #x = "//div[starts-with(@class, 'index_left')]//div[@class='ant-space-item']/span/text()"
        #pubtime = extractor.get_text(dom, x)
        #self.logger.info(f"parse_detail: publish time: {pubtime}")

        #x = "//div[starts-with(@class, 'index_cententWrapBox')]//text()"
        #article = extractor.get_text(dom, x)
        #self.logger.info(f"parse_detail: article: {article[:10]}")

        meta = response.meta

        item = {}
        item['anchor'] = meta['anchor']
        item['url'] =  meta['outlink']
        #item['title'] = title
        #item['author'] = author
        #item['pubtime'] = pubtime
        #item['article'] = article
        item['html'] = gzip.compress(response.body)
        item['encoding'] = self.encoding

        dic = {}

        dic['_db'] = 'dim_news'
        dic['_col'] = 'finance'
        dic['_item'] = item

        yield dic



