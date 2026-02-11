import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class GovCboSpider(CrawlSpider):

    name = "gov.cbo"
    redis_key = "gov.cbo"
    allowed_domains = ["cbo.gov"]

    def start_requests(self):
        copy_as_curl = """
        curl 'https://www.cbo.gov/publication/most-recent' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cache-control: max-age=0' \
  -H 'cookie: _ga=GA1.1.2028454886.1734947944; _ga_TMTDEKRHDC=GS1.1.1735006983.2.1.1735007726.0.0.0' \
  -H 'if-none-match: W/"1735007095"' \
  -H 'priority: u=0, i' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        """
        _, self.headers, _ = headers_to_dict(copy_as_curl)

        self.encoding = "utf-8"

        url = 'https://www.cbo.gov/publication/most-recent'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = '//h3/a'
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
