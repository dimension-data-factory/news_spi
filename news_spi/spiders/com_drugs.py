import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class ComDrugsSpider(CrawlSpider):

    name = "com.drugs"
    redis_key = "com.drugs"
    allowed_domains = ["drugs.com"]


    def start_requests(self):
        copy_as_curl = """
        curl 'https://www.cbsnews.com/us/' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"'
        """
        _, self.headers, _ = headers_to_dict(copy_as_curl)

        self.encoding = "utf-8"

        url = "https://www.cbsnews.com/us/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)


    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//div[@class='col-8 nocontent']//a[@class='item__anchor']"
        links = extractor.list_link_anchor(dom, x, response.request.url)
        if links:
            for href, anchor in links:
                self.logger.info(f"outlinks: {href}, {anchor}")
                meta = response.request.meta
                meta['anchor'] = anchor
                meta['outlink'] = href
                yield Request(url=href, callback=self.parse_detail, headers=self.headers, meta=meta)

    def parse_detail(self, response):

        html = response.body.decode(self.encoding)

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

