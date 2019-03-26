import requests
import requests_cache
import lxml.html

class FakePage(object):
    def __init__(self, url)
    self.name = "[NAME: {}]".format(url)
    self.url = url

def handle_lesson(page):
    r = requests.get(page.url).content
    root = lxml.html.fromstring(html)
    article = root.xpath("//article[@id='article']")
    # acquire videos and images, make nice CSS
    # <iframe src="youtube"></iframe>
    
    


sample_urls = [
    "https://www.mathplanet.com/education/pre-algebra/discover-fractions-and-factors/powers-and-exponents", # has video
    ]

for url in sample_urls:
    handle_lesson(FakePage(url))
    
