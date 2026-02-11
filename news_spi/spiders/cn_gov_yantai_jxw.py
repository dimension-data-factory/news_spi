import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class CnGovYantaiJxwSpider(scrapy.Spider):

    name = "cn.gov.yantai.jxw"

    redis_key = "cn.gov.yantai.jxw"

    allowed_domains = ["jxw.yantai.gov.cn"]

    def start_requests(self):

        self.encoding = "utf-8"

        block = """
        curl 'https://jxw.yantai.gov.cn/col/col2208/index.html' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"'
        """
        url, self.headers, _ = headers_to_dict(block)



        url = 'https://jxw.yantai.gov.cn/col/col2208/index.html'
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//div[@id='166972']/script"
        xml_content = dom.xpath(x)[0].text
        node_root = etree.HTML(xml_content)

        x = "//datastore/recordset/record/a"
        links = extractor.list_link_anchor(node_root, x, response.request.url)
        if links:
            for href, anchor in links:
                self.logger.info(f"outlinks: {href}, {anchor}")
                meta = response.request.meta
                meta['anchor'] = anchor
                meta['outlink'] = href
                yield Request(url=href, callback=self.parse_detail, headers=self.headers, meta=meta)

    def parse_detail(self, response):

        #print(response.body.decode(self.encoding))

        meta = response.meta

        item = {}
        item['anchor'] = meta['anchor']
        item['url'] =  meta['outlink']
        item['html'] = gzip.compress(response.body)
        item['encoding'] = 'utf-8'

        dic = {}

        dic['_db'] = 'dim_news'
        dic['_col'] = 'finance'
        dic['_item'] = item

        yield dic





