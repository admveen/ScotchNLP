import scrapy
from whiskeyscraper.items import WhiskeyItem
from scrapy.loader import ItemLoader

class WhiskyURLSpider(scrapy.Spider):
    name = 'whiskyurlspider'
    page_number = 2
    start_urls = ["https://www.masterofmalt.com/country-style/scotch/single-malt-whisky/1/"]

    def parse(self, response):
        
        for whisky_obj in response.css('div.boxBgr.product-box-wide.h-gutter.js-product-box-wide'):
            link_url = whisky_obj.css('div::attr(data-product-url)').get()
            # maybe put in whisky price here
            # whiskey_price = whisky_obj.css('div.product-box-wide-price gold::text').get()

            yield response.follow(link_url, callback=self.parse_whiskey)

        next_page = "https://www.masterofmalt.com/country-style/scotch/single-malt-whisky/" + str(WhiskyURLSpider.page_number) + "/"

        
        if next_page is not None:
            WhiskyURLSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse)
        
    """
        # this is for testing on a small number of pages.
        if WhiskyURLSpider.page_number <= 5:
            WhiskyURLSpider.page_number += 1
            yield response.follow(next_page, callback = self.parse) 
    """


    def parse_whiskey(self, response):

        wload = ItemLoader(item = WhiskeyItem(), selector = response)
        wload.add_css('name', 'h1.page_header::text')
        wload.add_css('nose', '#ContentPlaceHolder1_ctl00_ctl02_TastingNoteBox_ctl00_noseTastingNote::text')
        wload.add_css('palate', '#ContentPlaceHolder1_ctl00_ctl02_TastingNoteBox_ctl00_palateTastingNote::text')
        wload.add_css('finish', '#ContentPlaceHolder1_ctl00_ctl02_TastingNoteBox_ctl00_finishTastingNote::text')

        wload.add_css('description', 'div[itemprop="description"] p::text, div[itemprop="description"] p a::text')
        
        # creates a nested loader to extract info from the bottling details subsection
        details_loader = wload.nested_css('#whiskyDetailsWrapper')
        details_loader.add_css('region', '#ContentPlaceHolder1_ctl00_ctl00_wdRegion span.kv-val a::text')
        details_loader.add_css('style', '#ContentPlaceHolder1_ctl00_ctl00_wdStyle span.kv-val a::text')
        details_loader.add_css('distillery', '#ContentPlaceHolder1_ctl00_ctl00_wdDistillery span.kv-val a::text')
        details_loader.add_css('bottler', '#ContentPlaceHolder1_ctl00_ctl00_wdBottler span.kv-val::text')
        details_loader.add_css('age', '#ContentPlaceHolder1_ctl00_ctl00_wdYearsMatured span.kv-val a::text')
        details_loader.add_css('alcohol', '#ContentPlaceHolder1_ctl00_ctl00_wdAlcohol span.kv-val::text' )

        details_loader.add_css('maturation', '#ContentPlaceHolder1_ctl00_ctl00_wdMaturation span.kv-val::text' )
        details_loader.add_css('chill_filter', '#ContentPlaceHolder1_ctl00_ctl00_wdChillFiltered span.kv-val::text' )
        details_loader.add_css('cask_strength', '#ContentPlaceHolder1_ctl00_ctl00_wdNaturalStrengthCask span.kv-val::text' )


        return wload.load_item()
        

