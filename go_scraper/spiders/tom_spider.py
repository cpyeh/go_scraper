import scrapy
from go_scraper.items import GoRecordItem
class TomSpider(scrapy.Spider):
    """
    TomScraper
    """
    name = 'tom'
    encoding = 'gb2312'

    start_url = 'http://weiqi.tom.com/php/listqipu.html'
    start_urls = {'not_crawled': set([start_url]),
                  'crawled':set()}
    info_dict_transform = {'SZ':'BoardSize',
                           'C':'ExtraInfo',
                           'PW':'WhitePlayer',
                           'PB':'BlackPlayer',
                           'PC':'Location',
                           'KM': 'Komi',
                           'RE': 'GameResult',
                           'SO': 'Source',
                           'US': 'NoIdea',
                           'BR': 'BlackRank',
                           'WR': 'WhiteRank',
                           'DT': 'Date',
                           'EV': 'GameInfo',
                           'TM': 'GameTime'}
    ignore_info_set = set(['SO','US','SZ','C','TM'])
    crawled_num = 0
    def start_requests(self):
        """
        Each time add more url for future crawling if not already in the list
        """
        while self.start_urls['not_crawled'] and self.crawled_num < 1:
            url = self.start_urls['not_crawled'].pop()
            self.start_urls['crawled'].add(url)
            self.crawled_num += 1
            yield self.make_requests_from_url(url)

    def parse(self,response):
        """
        Add qipu_list page first, add them to the not_crawled_set
        Parse individual qipu
        """
        self.add_qipu_list(response)
        for href in response.css('.courselist ul li.c a::attr(href)'):
            url =  response.urljoin(href.extract()).replace('/..','')
            yield scrapy.Request(url, callback=self.parse_qipu_text)

    def add_qipu_list(self,response):
        for href in response.css('.pagenum a::attr(href)'):
            url = response.urljoin(href.extract())
            if url not in self.start_urls['crawled']:
                self.start_urls['not_crawled'].add(url)
                print url

    def parse_qipu_text(self,response):
        """
        Typical go record on TOM
        '(;EV[game_name]PB[black_player]PW[white_player]... ; B[];W[]...'
        1. remove unecessary (;
        2. parse info
        3. parse game
        """
        text = response.body.decode(self.encoding)#.decode("utf-8")
        if text.startswith("(;"):
            text = text[2:]
        print text
        qipu_dict = self.parse_info(text)
        if not qipu_dict:
            yield {}
        qipu_dict["GameRecord"] = self.parse_qipu(text)
        yield qipu_dict

    def parse_info(self, text):
        qipu_info_dict = {}
        qipu_info_str = text[:text.find(";")] +\
            text[text.rfind(";")+6:] # trailing info
        for i in qipu_info_str.split("]")[:-1]:
            k,v = i.split("[")
            if k == 'SZ' and int(v)<19:
                return {}
            if k in self.ignore_info_set or k not in self.info_dict_transform:
                continue
            qipu_info_dict[self.info_dict_transform[k]] = v
        return qipu_info_dict

    def parse_qipu(self, text):
        trailing_info_pos = text.rfind(";")+6
        qipu_str = text[text.find(";")+1:trailing_info_pos]
        return qipu_str
