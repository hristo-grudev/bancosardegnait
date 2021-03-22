import scrapy

from scrapy.loader import ItemLoader

from ..items import BancosardegnaitItem
from itemloaders.processors import TakeFirst

import requests

url = "https://istituzionale.bancosardegna.it/media-relations/comunicati-stampa?p_r_p_categoryId=override_1211849583"

payload = {}
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'X-Requested-With': 'XMLHttpRequest',
  'X-PJAX': 'true',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'Accept': '*/*',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://istituzionale.bancosardegna.it/media-relations/comunicati-stampa?p_r_p_categoryId=override_287207740',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'GUEST_LANGUAGE_ID=it_IT; ajs_user_id=null; ajs_group_id=null; _ga=GA1.2.882768449.1612958355; LPVID=kxYjU2N2YxMjJmNDgxYmNk; 01015-PRIVACY_READ=true; COOKIE_SUPPORT=true; 01015-IST-PRIVACY_READ=true; cookiesession1=678A3E0D01234JKLMNOPQRSTUVWXA8B6; ANONYMOUS_USER_ID=1236263845; LXpers=HP; pers_form_categoria=; pers_form_prodotto=; _gid=GA1.2.783890503.1616400368; LPSID-37544564=PZ00E0aMRL2_nQtkPBlYow; JSESSIONID=5D3E268390FA1B77E6FA3AA70A8AAD02.liferayprod1; last_3_page_id=["Istituzionale:Media","<font style="vertical-align: inherit; persist_page_id=Istituzionale:Media:Comunicati stampa; landing_page_id=Istituzionale:Media:Comunicati stampa; LFR_SESSION_STATE_20120=1616400868183; utag_main=v_id:01778bcf4df9001fc0e7ad24f94103072001d06a00bd0$_sn:3$_ss:0$_st:1616402668315$ses_id:1616400367726%3Bexp-session$_pn:5%3Bexp-session$_prevpage:Istituzionale%3AMedia%3AComunicati%20stampa%3Bexp-1616404468320'
}


class BancosardegnaitSpider(scrapy.Spider):
	name = 'bancosardegnait'
	start_urls = ['https://istituzionale.bancosardegna.it/media-relations/comunicati-stampa?p_r_p_categoryId=override_1211849583']

	def parse(self, response):
		data = requests.request("GET", response.url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)
		page_links = raw_data.xpath('//a[span[contains(@class,"filter-year")]]/@href').getall()
		for page in page_links:
			yield response.follow(page, self.parse_year)

	def parse_year(self, response):
		data = requests.request("GET", response.url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)
		post_links = raw_data.xpath('//div[@class="press-title-url"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		page_links = raw_data.xpath('//a[span[contains(@class,"filter-year")]]/@href').getall()
		for page in page_links:
			yield response.follow(page, self.parse_year)

	def parse_post(self, response):
		title = response.xpath('//div[@class="title"]/h1/text()').get()
		description = response.xpath('//div[@class="press-text"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//span[@class="date"]/text()').get()

		item = ItemLoader(item=BancosardegnaitItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
