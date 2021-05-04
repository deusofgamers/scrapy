# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import hashlib
import re
import time
from pathlib import Path

import dateparser
import requests
from pymongo import MongoClient

from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter

class TpdbPipeline:
    def process_item(self, item, spider):
        return item


class TpdbApiScenePipeline:
    def __init__(self, crawler):
        # db = MongoClient('mongodb://localhost:27017/')
        # self.db = db['scrapy']
        
        self.crawler = crawler
        
        if crawler.settings.get('path'):
            path = crawler.settings.get('path')
        else:
            path = crawler.settings.get('DEFAULT_EXPORT_PATH')

        if crawler.settings.get('file'):
            filename = crawler.settings.get('file')
            if "\\" not in filename and "/" not in filename:
                filename = Path(path, filename)
        else:
            filename = Path(path, crawler.spidercls.name + "_" + time.strftime("%Y%m%d-%H%M") + ".json")
        
        if crawler.settings.get('export'):
            if crawler.settings.get('export') == 'true':
                print (f"*** Exporting to file: {filename}")
                self.fp = open(filename, 'wb')
                self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    async def process_item(self, item, spider):
        ## So we don't re-send scenes that have already been scraped
        # if spider.force is not True:
        #     result = self.db.scenes.find_one({'url': item['url']})
        #     if result is not None:
        #         return

        payload = {
            'title': item['title'],
            'description': item['description'],
            'date': item['date'],
            'image': item['image'],
            'url': item['url'],
            'performers': item['performers'],
            'tags': item['tags'],
            'external_id': str(item['id']),
            'site': item['site'],
            'trailer': item['trailer'],
            'network': item['network']
        }

        headers = {
            "Authorization": "Bearer xxxx",
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'tpdb-scraper/1.0.0'
        }
        ## Post the scene to the API - requires auth with permissions
        # response = requests.post('https://api.metadataapi.net/scenes', json=payload, headers=headers)

        # url_hash = hashlib.sha1(str(item['url']).encode('utf-8')).hexdigest()

        # if response.status_code != 200:
        #     self.db.errors.replace_one({"_id": url_hash}, {
        #         'url': item['url'],
        #         'error': 1,
        #         'when': dateparser.parse('today').isoformat(),
        #         'response': response.json()
        #     }, upsert=True)
        # else:
        #     self.db.scenes.replace_one(
        #         {"_id": url_hash}, dict(item), upsert=True)

        if spider.settings.get('display') and spider.settings.get('LOG_LEVEL') == "INFO":
            if spider.settings.get('display')=="true":            
                titlelength = 60 - len(item['title'])
                if titlelength < 1:
                    titlelength = 1
                dispdate = re.search('(.*)T\d',item['date']).group(1)
                print (f"Item: {item['title']}" + " "*titlelength + f"{item['id']}\t{dispdate}\t{item['url']}")
        
        if spider.settings.get('export'):
            if spider.settings.get('export')=="true":
                self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        if spider.settings.get('export'):
            if spider.settings.get('export')=="true":
                self.fp.close()
        
