# -*- coding: utf-8 -*-
import scrapy


class GoRecordItem(scrapy.Item):
    BoardSize = scrapy.Field()
    WhitePlayer = scrapy.Field()
    BlackPlayer = scrapy.Field()
    GameResult = scrapy.Field()
    Location = scrapy.Field()
    Komi = scrapy.Field()
    Date = scrapy.Field()
    OtherInfo = scrapy.Field()
