import scrapy
from go_scraper.items import GoRecordItem


class SinaGoSpider(scrapy.Spider):
    """
    SinaScraper
    """
    name = 'sina_go'
    encoding = 'gbk'
    file_name = 'sina_go.json'
    start_urls = ['http://duiyi.sina.com.cn/gibo/new_gibo.asp?cur_page=%d' % i for i in range(0, 666)]
    cached_qipu_url = {}
    info_dict_transform = {'PW': 'WhitePlayer',
                           'WR': 'WhiteRank',
                           'PB': 'BlackPlayer',
                           'BR': 'BlackRank',
                           'RE': 'GameResult',
                           'TE': 'GameInfo',
                           'RD': 'Date',
                           'PC': 'Location',
                           'KO': 'Komi'}

    def parse(self, response):
        for href in response.css('.body_text1[bgcolor="#FFFFFF"] a::attr(href)'):
            qipu_url = href.extract().split("'")[1]
            if qipu_url not in self.cached_qipu_url:
                self.cached_qipu_url[qipu_url] = 1
                yield scrapy.Request(qipu_url, callback=self.parse_qipu_text)
            else:
                continue

    def parse_qipu_text(self, response):
        text = response.body.decode(self.encoding)
        info_blocks = text.split('\n')
        go_record_item = GoRecordItem()
        qipu_list = []
        for b in info_blocks:
            info_type = b[:2]
            if not info_type.startswith(';'):
                if info_type in self.info_dict_transform:
                    key = self.info_dict_transform[info_type]
                    value = b[b.find('[') + 1 : b.find(']')]
                    go_record_item[key] = value
            else:
                qipu_list.append(b.strip())
        game_record = ''.join(qipu_list)
        game_record = game_record[1:] if game_record.startswith(')') else game_record
        game_record = game_record[:-1] if game_record.endswith(')') else game_record
        go_record_item['GameRecord'] = game_record
        with open(self.file_name, 'a') as f:
            f.write(str(go_record_item).decode('unicode-escape').encode('utf-8')+'\n')
