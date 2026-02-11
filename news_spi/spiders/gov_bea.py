import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class GovBeaSpider(scrapy.Spider):

    name = "gov.bea"
    redis_key = "gov.bea"
    allowed_domains = ["bea.gov"]

    def start_requests(self):
        #-H 'if-modified-since: Tue, 24 Dec 2024 00:50:20 GMT' \
        # remove header above to avoid 304
        copy_as_curl = """
        curl 'https://www.bea.gov/news/current-releases' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cache-control: max-age=0' \
  -H 'cookie: _gid=GA1.2.192971146.1735013024; GUIDCookie=ee9c2086-42f3-462a-af89-055466e2d4b3; CFIWebMonPersistent-114=%7B%22LastAccept%22%3Anull%2C%22LastDecline%22%3A1735013063077%7D; RT="z=1&dm=bea.gov&si=lfte559y0rf&ss=m4xrpsjc&sl=0&tt=0"; _ga=GA1.2.58290498.1734760677; _ga_J4698JNNFT=GS1.1.1735024102.6.1.1735024331.11.0.0; CFIWebMonSession=%7B%22GUID%22%3A%229faf22ec-b1ba-976d-e861-734760678854%22%2C%22EmailPhone%22%3A%22%22%2C%22HttpReferer%22%3A%22https%3A//www.google.com.hk/%22%2C%22PageViews%22%3A22%2C%22CurrentRuleId%22%3A%22114%22%2C%22CurrentPType%22%3A%220%22%2C%22Activity%22%3A%22Browse%22%2C%22SessionStart%22%3A1734760678829%2C%22UnloadDate%22%3Anull%2C%22WindowCount%22%3A3%2C%22LastPageStayTime%22%3A2092153%2C%22AcceptOrDecline%22%3A%7B%22114%22%3A%22D%22%7D%2C%22FirstBrowsePage%22%3A%22https%3A//www.bea.gov/news/glance%22%2C%22FirstBrowseTime%22%3A1735024207217%2C%22FinallyLeaveTime%22%3A1735024315200%2C%22FinallyBrowsePage%22%3A%22https%3A//www.bea.gov/news/archive%3Ffield_related_product_target_id%3DAll%26created_1%3DAll%26title%3D%22%2C%22SiteReferrer%22%3A%22https%3A//www.bea.gov/news/current-releases%22%2C%22LastPopUpPage%22%3A%22https%3A//www.bea.gov/%22%2C%22TimeSpentonSite%22%3A0%2C%22GoogleAnalyticsValue%22%3A%22ee9c2086-42f3-462a-af89-055466e2d4b3%22%2C%22Dimension%22%3A%22%22%2C%22CookiePath%22%3A%22/%3B%20Secure%3B%22%2C%22AdditionalAttributes%22%3A%7B%7D%2C%22ClickTracker%22%3A%22url%3Dhttps%253A%252F%252Fwww.bea.gov%252F%26p%3D0%26elapsed%3D2327976ms%26movement%3D8812px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fdata%252Fgdp%26p%3D1%26elapsed%3D95192676ms%26movement%3D9222px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252F%26p%3D2%26elapsed%3D134578ms%26movement%3D8121px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fglance%26p%3D3%26elapsed%3D28815ms%26movement%3D2973px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252F2024%252Fgross-domestic-product-state-and-personal-income-state-3rd-quarter-2024%26p%3D4%26elapsed%3D100122ms%26movement%3D2471px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fschedule%26p%3D5%26elapsed%3D6838ms%26movement%3D848px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fblog%26p%3D6%26elapsed%3D10874ms%26movement%3D611px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fblog%252F2024-12-20%252Fpersonal-income-and-outlays-november-2024%26p%3D7%26elapsed%3D17528ms%26movement%3D1284px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fblog%26p%3D8%26elapsed%3D7920ms%26movement%3D849px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Farchive%253Ffield_related_product_target_id%253DAll%2526created_1%253DAll%2526title%253D%26p%3D9%26elapsed%3D16824ms%26movement%3D1024px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fcurrent-releases%26p%3D10%26elapsed%3D6748ms%26movement%3D708px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Ffor-journalists%26p%3D11%26elapsed%3D58542ms%26movement%3D4069px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fcurrent-releases%26p%3D12%26elapsed%3D10627956ms%26movement%3D7333px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fblog%26p%3D13%26elapsed%3D10644119ms%26movement%3D2247px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%26p%3D14%26elapsed%3D10948029ms%26movement%3D928px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fcurrent-releases%26p%3D15%26elapsed%3D10904448ms%26movement%3D860px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fglance%26p%3D16%26elapsed%3D6255ms%26movement%3D1736px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fcurrent-releases%26p%3D17%26elapsed%3D1528ms%26movement%3D0px%7Curl%3Dhttps%253A%252F%252Fwww.bea.gov%252Fnews%252Fschedule%26p%3D18%26elapsed%3D42764ms%26movement%3D4379px%22%2C%22PageIndex%22%3A19%2C%22AllCookies%22%3A%22%22%2C%22AllCustomVariables%22%3A%22%22%7D' \
  -H 'if-none-match: "1735001420-gzip"' \
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

        url = "https://www.bea.gov/news/current-releases"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.bea.gov/news/blog"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//tr[@class='release-row']/td/a|//h3[@class='blog-post-title']/a"
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




