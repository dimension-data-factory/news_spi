import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class ComLeiphoneSpider(CrawlSpider):

    name = "com.leiphone"
    redis_key = "com.leiphone"

    def start_requests(self):
        self.headers = {}
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        self.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        self.headers['Connection'] = 'keep-alive'
        self.headers['Cookie'] = 'PHPSESSID=8bf49627c95589d9025336bba9363b38; SameSite=None; Hm_lvt_0f7e8686c8fcc36f05ce11b84012d5ee=1696641560; Hm_lpvt_0f7e8686c8fcc36f05ce11b84012d5ee=1696642349'
        self.headers['Referer'] = 'https://www.leiphone.com/category/5ggy'
        self.headers['Sec-Fetch-Dest'] = 'document'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['Sec-Fetch-User'] = '?1'
        self.headers['Upgrade-Insecure-Requests'] = '1'
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        self.headers['sec-ch-ua'] = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers['sec-ch-ua-mobile'] = '?0'
        self.headers['sec-ch-ua-platform'] = '"Windows"'

        self.encoding = 'utf-8'

        urls = [
                'https://www.leiphone.com/category/industrynews',
                'https://www.leiphone.com/category/ai',
                'https://www.leiphone.com/category/transportation',
                'https://www.leiphone.com/category/digitalindustry',
                'https://www.leiphone.com/category/fintech',
                'https://www.leiphone.com/category/aihealth',
                'https://www.leiphone.com/category/chips',
                'https://www.leiphone.com/category/gbsecurity',
                'https://www.leiphone.com/category/smartcity',
                'https://www.leiphone.com/category/industrycloud',
                'https://www.leiphone.com/category/IndustrialInternet',
                'https://www.leiphone.com/category/iot',
                ]
        for url in urls:
            yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)


    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//ul[@class='clr']/li//h3/a"
        links = extractor.list_link_anchor(dom, x, response.request.url)
        if links:
            for href, anchor in links:
                self.logger.info(f"outlinks: {href}, {anchor}")
                meta = response.request.meta
                meta['anchor'] = anchor
                meta['outlink'] = href
                yield Request(url=href, callback=self.parse_detail, headers=self.headers, meta=meta)


    def parse_detail(self, response):

        #html = response.body.decode("utf-8")
        #dom = etree.HTML(html)


        #x = '//h1//text()'
        #title = gettext(dom, x)
        #self.logger.info(f"parse_detail: title: {title}")

        #x = "//td[@class='aut']/a"
        #href, author = getlink(dom, x, response.request.url)
        #self.logger.info(f"parse_detail: author: {author}, {href}")

        #x = "//td[@class='time']//text()"
        #pubtime = gettext(dom, x)
        #self.logger.info(f"parse_detail: publish time: {pubtime}")

        #x = "//div[@class='lph-article-comView']//text()"
        #article = gettext(dom, x)
        #self.logger.info(f"parse_detail: article: {article}")


        meta = response.meta

        item = {}
        item['anchor'] = meta['anchor']
        item['url'] =  meta['outlink']
        #item['title'] = title
        #item['pubtime'] = pubtime
        #item['article'] = article
        item['html'] = gzip.compress(response.body)
        item['encoding'] = self.encoding

        dic = {}

        dic['_db'] = 'dim_news'
        dic['_col'] = 'finance'
        dic['_item'] = item

        yield dic







