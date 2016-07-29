# -*- coding: utf-8 -*-
import scrapy


class GoRecordItem(scrapy.Item):
    BoardSize = scrapy.Field()
    WhitePlayer = scrapy.Field()
    WhiteRank = scrapy.Field()
    BlackPlayer = scrapy.Field()
    BlackRank = scrapy.Field()
    GameRecord = scrapy.Field()
    GameResult = scrapy.Field()
    GameInfo = scrapy.Field()
    Date = scrapy.Field()
    Location = scrapy.Field()
    Komi = scrapy.Field()

