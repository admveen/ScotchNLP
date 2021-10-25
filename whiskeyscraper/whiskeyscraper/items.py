# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags


class WhiskeyItem(scrapy.Item):
    # name and tasting notes:
    name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    description = scrapy.Field(input_processor = MapCompose(str.strip), output_processor = Join())
    nose = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    palate = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    finish = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())

    # whiskey bottling details 

    region = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    style = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    distillery = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    bottler = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    age = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    alcohol = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    price = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    # These sometimes appear in the bottling details. Other times they appear in the description and will have to be extracted via text-processing later.

    maturation = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    chill_filter = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    cask_strength = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())



    



