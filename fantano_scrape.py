import scrapy

class FantanoSpider(scrapy.Spider):
    name = "fantano_spider"
    start_urls = ["https://www.youtube.com/user/theneedledrop/videos"]
    

    def parse(self, response):
        title_boxes = '.yt-simple-endpoint'
        t = response.xpath("//a[@id=video_title]")
        print("\n\n\n\n",t,"\n\n\n")
               