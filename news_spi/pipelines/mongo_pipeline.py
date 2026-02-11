# -*- coding: utf-8 -*-
import pymongo
import redis
import time

class GMongoPipeline(object):

    def __init__(self, mongo_cli, redis_cli):
        self.mongo_cli = mongo_cli
        self.redis_cli = redis_cli

    @classmethod
    def from_settings(cls, settings):

        # 写入配置文件
        mongodb_con_str = settings.get("MONGODB_CON_STR")
        mongo_cli = pymongo.MongoClient(mongodb_con_str)

        redis_con_str = settings.get("REDIS_URL")
        redis_cli = redis.from_url(redis_con_str)
        return cls(mongo_cli, redis_cli)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, dic, spider):
        if '_db' in dic:
            _db = dic.get('_db')
            _col = dic.get('_col')
            item = dic.get('_item')

            item['domain'] = spider.name
            item['fetch_time'] = int(time.time())

            db = self.mongo_cli[_db]
            col = db[_col]
            result = col.insert_one(item)

            # 加入html normalization 管道
            self.redis_cli.rpush('news_pipe', str(result.inserted_id))

        return item


    def close_spider(self, spider):
        print('closing mongo db pipeline....')
