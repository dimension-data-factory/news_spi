import gzip
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
import news_spi.utils.extractor as extractor
from news_spi.utils.base import headers_to_dict


class OrgNprSpider(CrawlSpider):

    name = "org.npr"
    allowed_domains = ["npr.org"]

    def start_requests(self):
        copy_as_curl = """
        curl 'https://www.npr.org/sections/business/' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cache-control: max-age=0' \
  -H 'cookie: usprivacy=1---; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIBYB2AZgAYATFwECArAE4AHFw4dxPAIwiQAXyA; cebs=1; _pc_Referral=true; optimizelyEndUserId=oeu1734760329097r0.9229504483897479; permutive-id=89d17fe8-017c-4ec6-a115-cee6e9948ccb; _cb=DsQwyiCqQ-q3Mht8y; __pdst=84f27d0b88f04a149a63d177c8c8ce94; _cc_id=d682fd5dfd134fbd9bef52f319f1dba3; OptanonAlertBoxClosed=2024-12-21T06:23:17.550Z; OneTrustWPCCPAGoogleOptOut=false; _pbjs_userid_consent_data=3524755945110770; vuukle_geo_region={%22country_code%22:%22HK%22%2C%22os%22:%22Mac%20OS%20X%22%2C%22device%22:%22Tablet%22%2C%22browser%22:%22Chrome%22}; uid-s=26539f2-310e-4ab2-a69b-385ff01e6482; vsid=d10ee882-07b0-42da-9e97-b144ca1c415e; ak_bmsc=EFFE0333B4A4433AB5DA47E72AC211E2~000000000000000000000000000000~YAAQiqwwFz7XdO6TAQAAlRe49xqRZTSWpwZPzXb2FYeQSUVb0zyZzLh7tr8f2QBBX0n6fBSx37b9/Pj99rVV/vrj1dd6XWqxJsUTacBUfe6nsAfWA8rV8/VuOEJrwi81gXCob5kaezngermFlsu5hV6fNXf46UWCz/vFT8I2e9etaDkML9NOB9i5Pj44TT104LKui3Zr14JM7GOZfNXRXUR1S1bzndpdsYTvn/tvuw24QtckmBydC14tVsysCDEJer/eNVsDisUksRqbBPWGQ9eh4aWcqK4/qI4cpzyhsdJCkp2UgcDMAF97xfW8Zvt+GbKGgi8tXB7FbgpGHVgf3c0bTBlX7TLBcl0SZD4NM2YUo4xAGzRUomJFP/ATlA7986GDvrYt; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAEzIBYB2AZgAYATFwECArAE4AHFw4dxPAIwiQAXyA; _pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1vdXQifSwiMSI6eyJtb2RlIjoib3B0LW91dCJ9LCIyIjp7Im1vZGUiOiJvcHQtb3V0In0sIjMiOnsibW9kZSI6Im9wdC1vdXQifSwiNCI6eyJtb2RlIjoib3B0LW91dCJ9LCI1Ijp7Im1vZGUiOiJvcHQtb3V0In0sIjYiOnsibW9kZSI6Im9wdC1vdXQifSwiNyI6eyJtb2RlIjoib3B0LW91dCJ9fSwicHVycG9zZXMiOm51bGx9; _gid=GA1.2.1505468449.1735027935; _pubcid=c9baba95-a986-49d1-b06a-31d2b9772e98; _pubcid_cst=VyxHLMwsHQ%3D%3D; _lr_retry_request=true; _lr_env_src_ats=false; panoramaId_expiry=1735114416039; panoramaId=6115d050bb29dde3b2196106b857a9fb927a053b1300e88f352bb81584c346d7; pbjs-unifiedid=%7B%22TDID%22%3A%227ab9c8bd-2acd-4d77-8652-e0a3c3719ae3%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222024-11-24T08%3A13%3A41%22%7D; pbjs-unifiedid_cst=VyxHLMwsHQ%3D%3D; _ce.clock_data=-135%2C185.217.5.85%2C1%2C0845b309c7b9b957afd9ecf775a4c21f%2CChrome%2CSG; __pnahc=0; __stripe_mid=9f8e14ca-a54b-4fe7-bbf5-bc66d6ec320f8e82b3; __stripe_sid=02a705ef-4a5a-4457-96e5-9f5f2c70398a8574a1; cX_G=cx%3A109ck3c7u4h4r3oio07fkafmc7%3A3b2wk1e8whh6w; _cb_svref=external; __gads=ID=8757b92362e9860b:T=1734762200:RT=1735028463:S=ALNI_MazY-9iI6Z_2t7oM8jktxTPcEt0IQ; __gpi=UID=00000faff4eda26d:T=1734762200:RT=1735028463:S=ALNI_MaVpEwitCpEI8QtevNcDWuhhJlvqA; __eoi=ID=7592636aa9da3b52:T=1734762200:RT=1735028463:S=AA-AfjZipJdQJ2p6Y6VZBiIo0IQo; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Dec+24+2024+16%3A21%3A41+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202405.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=6800cba1-ecbc-44ce-8096-76a0e148b4fa&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=%3B&AwaitingReconsent=false; _pcid=%7B%22browserId%22%3A%22m526vneqss2c1erl%22%7D; _pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1pbiJ9LCIxIjp7Im1vZGUiOiJvcHQtaW4ifSwiMiI6eyJtb2RlIjoib3B0LWluIn0sIjMiOnsibW9kZSI6Im9wdC1pbiJ9LCI0Ijp7Im1vZGUiOiJvcHQtaW4ifSwiNSI6eyJtb2RlIjoib3B0LWluIn0sIjYiOnsibW9kZSI6Im9wdC1pbiJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjpudWxsfQ%3D%3D; __adblocker=false; cebsp_=7; bm_sv=7A6BF40565D85EA76128DE20EB1401EE~YAAQHr3VPWLAwrmTAQAAXPHB9xpUvElzjqgf5S6ohukcAi3Eq7J4+PvDotWvA7b+KFdyPvDbWeQf5c/S8UbouTife03jBySVA+NWDQSjFv9aLVhIcPYrG+eJL3Yh94AUMddARIBNyxMPaD8kbYZuRd/mDVm8QC+xn60CB6zX3czhVubc4nh1tN3A4PISR+CEJtAvxqlXt8cIzhZySN97ntRdAxfH3hCpWkNHFZdl2RFMk446DpvxHLEuvSwP+Q==~1; __tbc=%7Bkpex%7DUCs-ZgOOgItjFt7K-d2laOG54dzO61vUoThlwT7pgoqg8Hoq5HfmETc3Me5lzgiD; __pat=-18000000; __pvi=eyJpZCI6InYtbTUyNzY4M2RidzYycGFmayIsImRvbWFpbiI6Ii5ucHIub3JnIiwidGltZSI6MTczNTAyODUwMzUwMn0%3D; xbc=%7Bkpex%7DOlUYx7oCf1Ze16xoJSt4Q6LFRqwGcJ-HCBmC9ieaSm0y3jpaTTkoLFhLrNcRiDTZICs-yYWfduBsrFIKFAi4og_BO61XYqzUHDqVwBsE7EcoNbJTUd29kB7wGBK4McCmzr0-Y60YfRoasrEzTLCchhT0IdbkwPTQ5o1O5TduZ4nEPGL79DfGaHT2e73Nz8-p3sA3dw19qunlRN7ek9GLLX_W9XAOgHwFLhGcIcgeUdybHI8sbE-ENMsZD0atwxs1; _pcus=eyJ1c2VyU2VnbWVudHMiOnsiQ09NUE9TRVIxWCI6eyJzZWdtZW50cyI6WyJMVHM6OTNjYmMwYTQ2YjkyMTdjM2RmODMwY2MyZWRmMzNjZWRkZjUwYmJkZTo1IiwiQ1Njb3JlOjU2NmU4YmM5YWI4YWRjZDdlMTFmOWEwOWJiOGZkYTNhMTAzNzc4YjA6OCIsIkxUcmV0dXJuOjgxMzZhYWRhNGY5NzQyYzI2MWZjN2QyMDBhY2M1YzJlZDE1ODllN2E6MCJdfX19; _ga_XK44GJHVBE=GS1.1.1735027930.6.1.1735028506.17.0.0; _chartbeat2=.1734760346271.1735028506306.1001.BlaDrMBBeMejClIOUHBL1RavC1NHqg.4; cX_P=m526vneqss2c1erl; _ga=GA1.2.1835921826.1734760341; cto_bundle=Mz1zKV9JWVpXUzZ3N3hleG9wRCUyRnc5VEk2WmtiMTExaTdOT2hLRlJ3NjYwRUN3U3F4WHg0T0d3cVJhbEVoSWJXbmJabHh1bkhPTUxPb2ptS1lvb2JDQ1Bmd0hYUU5zMTQzY3hMU3N3aE82RXZKR3V2alVqT1BkMmR3UTV5QVFYb2s0UlFTVkFwUlExbDVUczI1Y3pRM0wzTlFmUWhUUnlRRTIwbDVJdiUyQjd0Tzk0S0g5dzY5b2hDSVBUUkpZU1VSd04lMkYyRTY; cto_bidid=f9hq6l9DWHEwRjdKejFuJTJGYjRtcFdndXJqOWdHYWUzVVJnJTJCZXJBWFNzMWdja0FPWGVldyUyQlRya0o1RkN2UjU4OEdDZ3ZGbE1hSzI4RmF1NEFlZkFDMzNlMXpGVEJIb1E3RGIyeklKOUdpZmFDTUJvSTkwTmU4NmpTbDFuNlREZFpVZ1lWZ3JyMWtnMU1CcFhvamhWbHNtNWxnMkElM0QlM0Q; _dd_s=rum=0&expire=1735029528858; RT="z=1&dm=www.npr.org&si=f253fa5f-5b80-482e-b958-3f852154cf71&ss=m526ryq5&sl=5&tt=21e5&bcn=%2F%2F684d0d42.akstat.io%2F&obo=1&ld=hene&r=48qow1y6&ul=heng"; _ce.s=v~d4ecb21dfccec792abaea3e54170b179ca829be2~lcw~1735028646507~vir~returning~lva~1735028052134~vpv~0~v11.cs~452995~v11.s~182a9690-c1cf-11ef-8e88-2ddc5fc1484a~v11.sla~1735028646506~gtrk.la~m5279b58~v11.send~1735028648717~lcw~1735028648718' \
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

        url = "https://www.npr.org/sections/national/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/business/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/politics/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/business/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/climate/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/science/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/health/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        url = "https://www.npr.org/sections/climate/"
        yield Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)


    def parse(self, response):

        html = response.body.decode(self.encoding)
        dom = etree.HTML(html)

        x = "//h2[@class='title']/a"
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

