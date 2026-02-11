import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class ComJiemianSpider(CrawlSpider):

    name = "com.jiemian"
    redis_key = "com.jiemian"

    def start_requests(self):
        self.headers = {}
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        self.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        self.headers['Cache-Control'] = 'max-age=0'
        self.headers['Connection'] = 'keep-alive'
        self.headers['Cookie'] = 'PHPSESSID=0l7vk5br63ri4nasikv19e9jj0; SERVERID=papi131; __utrace=a5d75ad5dfd9b700a766a1132c9f7853; br-client=02b33327-663f-44e3-be18-c96987925b54; br-session-82=4ac96eff-1202-427a-bad9-a1c93b16ea90|1696752248072|1696752277740|13'
        self.headers['Sec-Fetch-Dest'] = 'document'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'none'
        self.headers['Sec-Fetch-User'] = '?1'
        self.headers['Upgrade-Insecure-Requests'] = '1'
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        self.headers['sec-ch-ua'] = '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        self.headers['sec-ch-ua-mobile'] = '?0'
        self.headers['sec-ch-ua-platform'] = '"Windows"'

        self.encoding = 'utf-8'

        urls = [
                'https://m.jiemian.com/lists/65_1.html',
                'https://m.jiemian.com/lists/4_1.html',
                'https://m.jiemian.com/lists/51_1.html',
                'https://m.jiemian.com/lists/112_1.html',
                'https://m.jiemian.com/lists/9_1.html',
                'https://m.jiemian.com/lists/31_1.html',
                'https://m.jiemian.com/lists/28_1.html',
                'https://m.jiemian.com/lists/30_1.html',
                'https://m.jiemian.com/lists/86_1.html',
                'https://m.jiemian.com/lists/49_1.html',
                'https://m.jiemian.com/lists/141_1.html',
                'https://m.jiemian.com/lists/410_1.html',
                'https://m.jiemian.com/lists/472_1.html',
                'https://m.jiemian.com/lists/703_1.html',
                'https://m.jiemian.com/lists/712_1.html',
                'https://m.jiemian.com/lists/605_1.html',
                ]
        for url in urls:
            yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)




    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//h3/a|//p/a"
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

        #x = "//div[@class='user-title']//text()"
        #author = gettext(dom, x)
        #self.logger.info(f"parse_detail: author: {author}")

        ##x = "//span[starts-with(@class, 'title-icon-item')]/text()"
        ##pubtime = gettext(dom, x)
        ##self.logger.info(f"parse_detail: publish time: {pubtime}")

        #x = "//div[@class='article-content ']//text()"
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
