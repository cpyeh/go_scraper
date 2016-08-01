import scrapy
import pandas as pd
from functools import partial
import requests
from go_scraper.items import GoRecordItem


class Web2GoSpider(scrapy.Spider):
    """
    TomScraper
    TODO: add structure to each game
    """
    name = 'web2go'
    encoding = 'big5'
    start_urls = ['http://web2go.board19.com/gopro/pro_list.php?ar=%s' % c for c in ['CN', 'JP', 'KR', 'TW']]

    player_base_url = "http://web2go.board19.com/gopro/psnx_list.php?id=%s"
    qipu_info_dict = {}

    qipu_crawled = set()
    qipu_not_crawled = set()
    qipu_base_url = "http://web2go.board19.com/test/getsgf.php?fn=%s"

    info_field = ['WhitePlayer', 'BlackPlayer', 'GameResult', 'GameInfo', 'Date']

    def parse(self, response):
        player_ids = self.get_player_id(response)
        print player_ids

        for player_id in player_ids:
            player_url = self.player_base_url % player_id
            self.add_qipu(player_url)
        print self.qipu_not_crawled

        while self.qipu_not_crawled:
            qipu_id = self.qipu_not_crawled.pop()
            if qipu_id not in self.qipu_crawled:
                self.qipu_crawled.add(qipu_id)
                qipu_url = self.qipu_base_url % qipu_id
                parse_qipu_by_id = partial(self.parse_qipu, id=qipu_id)
                yield scrapy.Request(qipu_url, callback=parse_qipu_by_id)
            else:
                continue

    @staticmethod
    def get_player_id(response):
        player_ids = []
        #id_base_url = 'http://web2go.board19.com/gopro/psn_list.php?id='
        id_base_url = 'psn_list.php?id='
        for href in response.css('tbody td a::attr(href)'):
            url = href.extract()
            if url.startswith(id_base_url):
                player_ids.append(url.replace(id_base_url, ''))
        return player_ids

    def add_qipu(self, player_url):
        """
        :param response:
        :return:
        Get gipu id add to qipu_not_crawled and get info and add to qipu_info
        """

        response = requests.get(player_url)
        response_body = response.text
        start = response_body.find('<table')
        end = response_body.find('/table>')
        table_html = response_body[start:end+7]

        qipu_df = pd.read_html(table_html, encoding=self.encoding, header=0)[0]
        qipu_df.columns = ['No', 'qipu_id', 'BlackPlayer', 'WhitePlayer', 'Date',
                           'Age', 'GameResult', 'NumberOfMoves', 'GameInfo']
        for _,qipu_row_dict in qipu_df.iterrows():
            qipu_id = qipu_row_dict['qipu_id']
            self.qipu_not_crawled.add(qipu_id)
            self.qipu_info_dict[qipu_id] = qipu_row_dict

    def parse_qipu(self, response, id):
        text = response.body.decode(self.encoding)
        go_record_item = GoRecordItem()
        go_record_item['GameRecord'] = self.parse_qipu_text(text)
        for key in self.info_field:
            go_record_item[key] = self.qipu_info_dict[id][key]
        print go_record_item
        yield go_record_item

    @staticmethod
    def parse_qipu_text(text):
        start = text.find(';') + 1
        end = text.find(';', start)
        return text[start: end]