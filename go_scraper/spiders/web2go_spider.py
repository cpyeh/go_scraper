import scrapy

class Web2GoSpider(scrapy.Spider):
    """
    TomScraper
    TODO: add structure to each game
    """
    name = 'web2go'
    encoding = 'big5'
    web2go_base_url = 'http://web2go.board19.com/gopro/yymm_list.php' +\
        '?id=%d-%02d'
    start_urls = [ web2go_base_url%(i,j)
        for i in range(1991,2001)
        for j in range(1,13)]

    def start_requests(self):
        yield self.make_requests_from_url(url)

    def parse(self,response):
        """
        Add qipu_list page first, add them to the not_crawled_set
        Parse individual qipu
        """
        self.add_qipu_list(response)
        #for href in response.css('.courselist ul li.c a::attr(href)'):
        #    url =  response.urljoin(href.extract()).replace('/..','')
        #    yield scrapy.Request(url, callback=self.parse_qipu_text)

    def add_qipu_list(self,response):
        for href in response.css('.pagenum a::attr(href)'):
            url = response.urljoin(href.extract())
            if url not in self.start_urls['crawled']:
                self.start_urls['not_crawled'].add(url)
                print url

    def parse_qipu_text(self,response):
        """
        1. remove unecessary
        2. parse info
        3. parse game
        """
        text = response.body.decode(self.encoding)#.decode("utf-8")
        if text.startswith("(;"):
            text = text[2:]
        print text
        qipu_dict = self.parse_info(text)
        qipu_dict["GameRecord"] = self.parse_qipu(text)
        yield qipu_dict

    def parse_info(self, text):
        qipu_info_dict = {}
        qipu_info_str = text[:text.find(";")] +\
            text[text.rfind(";")+6:] # trailing info
        for i in qipu_info_str.split("]")[:-1]:
            k,v = i.split("[")
            if k in ignore_info_set:
                continue
            qipu_info_dict[info_dict_transform[k]] = v
        return qipu_info_dict

    def parse_qipu(self, text):
        trailing_info_pos = text.rfind(";")+6
        qipu_str = text[text.find(";")+1:trailing_info_pos]
        return qipu_str
