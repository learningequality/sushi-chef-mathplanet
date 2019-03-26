import requests
import requests_cache
import lxml.html
from bs4 import BeautifulSoup
import localise
with open("template.html") as f:
    template=f.read()

class FakePage(object):
    def __init__(self, url):
        self.name = "[NAME: {}]".format(url)
        self.url = url
    
def get_video_node(url):
    # TODO
    return "Node", "sha1"

def handle_lesson(page):
    video_nodes = []
    images = []
    html = requests.get(page.url).content
    root = lxml.html.fromstring(html)
    article = root.xpath("//article[@id='article']")[0]
    videos = article.xpath("//iframe")
    images = article.xpath("//img")
    for video in videos:
        node, nodehash = get_video_node(video.attrib['src'])
        video.attrib['src'] = "/content/storage/{}/{}/{}.mp4".format(nodehash[0], nodehash[1], nodehash)
        
    new_html = template.replace("{name}", page.name).replace("{article}", lxml.html.tostring(article).decode('utf-8'))
    local_soup = localise.make_local_html(BeautifulSoup(new_html, "html5lib"), page.url)
    return local_soup, video_nodes
    # acquire videos and images, make nice CSS
    # <iframe src="youtube"></iframe>
    
    


sample_urls = [
    "https://www.mathplanet.com/education/pre-algebra/discover-fractions-and-factors/powers-and-exponents", # has video
    ]

for url in sample_urls:
    print(handle_lesson(FakePage(url)))
    
