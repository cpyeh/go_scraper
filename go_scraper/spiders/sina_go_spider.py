import scrapy

class SinaGoSpider(scrapy.Spider):
    """
    SinaScraper
    """
    name = 'sina_go'
    encoding = 'gb2312'
    sinago_base_url = 'http://duiyi.sina.com.cn/gibo/new_gibo.asp?cur_page=%d'
    #start_urls = [ sinago_base_url%i for i in range(0,666)]
    start_urls = [ sinago_base_url%i for i in range(1)]
    info_dict_transform = {'TE': 'GameInfo',
                           'RD': 'Date',
                           'PW':'WhitePlayer',
                           'PB':'BlackPlayer',
                           'PC':'Location',
                           'KO': 'Komi',
                           'RE': 'GameResult',
                           'BR': 'BlackRank',
                           'WR': 'WhiteRank',
                           }

    def parse(self,response):
        """
        Add qipu_list page first, add them to the not_crawled_set
        Parse individual qipu
        """
        for href in response.css('.body_text1[bgcolor="#FFFFFF"]:nth-child(2) a::attr(href)'):
            url =  href.extract().split("'")[1]
            yield scrapy.Request(url, callback=self.parse_qipu_text)

    def parse_qipu_text(self,response):
        """
        1. remove unecessary
        2. parse info
        3. parse game
        """
        text = response.body.decode(self.encoding)
        info_blocks = text.split('\n')
        print text
        qipu_dict = {}
        qipu_list = []
        for b in info_blocks:
            info_type = b[:2]
            if not info_type.startswith(';'):
                if info_type in self.info_dict_transform:
                    key = self.info_dict_transform[info_type]
                    value = b[b.find('[') + 1 : b.find(']')]
                    qipu_dict[key] = value
            else:
                qipu_list.append(b.strip())
        game_record = ''.join(qipu_list)
        game_record = game_record[1:] if game_record.startswith(')') else game_record
        game_record = game_record[:-1] if game_record.endswith(')') else game_record
        qipu_dict['GameRecord'] = game_record
        yield qipu_dict
