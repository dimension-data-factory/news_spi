import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class CnGovYantaiFgwSpider(scrapy.Spider):

    name = "cn.gov.yantai.fgw"

    redis_key = "cn.gov.yantai.jxw"

    allowed_domains = ["fgw.yantai.gov.cn"]

    def start_requests(self):

        self.encoding = "utf-8"

        block = """
        curl 'https://fgw.yantai.gov.cn/col/col52218/index.html' \
  -H 'Referer: https://fgw.yantai.gov.cn/col/col52218/index.html' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"'
        """
        url, self.headers, _ = headers_to_dict(block)
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):
        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//div[@id='154360']//script"
        xml_content = dom.xpath(x)[0].text

        arr = xml_content.split(";")
        for i, line in enumerate(arr):
            if line.startswith("url"):
                href = line[8:].strip("'")
                if href.startswith("http"):
                    continue
                if href.startswith("/"):
                    href = 'https://fgw.yantai.gov.cn' + href
                else:
                    href = 'https://fgw.yantai.gov.cn/' + href
                anchor = arr[i+1][11:].strip('"')
                self.logger.info(f"outlinks: {href}, {anchor}")

                meta = response.request.meta
                meta['anchor'] = anchor
                meta['outlink'] = href

                yield Request(url=href, callback=self.parse_detail, headers=self.headers, meta=meta)


    def parse_detail(self, response):

        #html = response.body.decode("utf-8")

        #dom = etree.HTML(html)
        #x = "//meta[@name='ArticleTitle']/@content"
        #title = dom.xpath(x)[0]
        #print('title', title)

        #x = "//meta[@name='pubdate']/@content"
        #pubtime = dom.xpath(x)[0]
        #pubtime = extractor.get_time(pubtime)
        #print('pubtime', pubtime)

        #x = "//div[@id='zoom']//text()"
        #article_md, article = extractor.get_markdown_text(dom, x)

        #print('article', article)


        meta = response.meta

        item = {}
        item['anchor'] = meta['anchor']
        item['url'] =  meta['outlink']
        item['html'] = gzip.compress(response.body)
        item['encoding'] = self.encoding

        dic = {}

        dic['_db'] = 'dim_news'
        dic['_col'] = 'finance'
        dic['_item'] = item

        yield dic

