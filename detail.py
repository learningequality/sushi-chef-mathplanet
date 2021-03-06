import requests
import requests_cache
import lxml.html
import hashlib
import shutil
import os
from bs4 import BeautifulSoup
from ricecooker.classes.files import WebVideoFile, HTMLZipFile
from ricecooker.classes.nodes import VideoNode, HTML5AppNode
from le_utils.constants.licenses import CC_BY_NC_ND

import localise
import tex_to_svg
from youtube_dl import YoutubeDL

def youtube_info(url):
    with YoutubeDL() as ydl:
        return ydl.extract_info(url, download=False) # url, id, title

class FakePage(object):
    def __init__(self, url):
        self.name = "[NAME: {}]".format(url)
        self.url = url

def get_video_node(url):
    wvf = WebVideoFile(url, high_resolution=False)
    info = youtube_info(url) # {id, title}
    node = VideoNode(source_id=info['id'], title=info['title'], license=CC_BY_NC_ND, copyright_holder="Mathplanet", files=[wvf])
    return node, wvf.get_filename()

def handle_lesson(page):
    def makefolder():
        os.mkdir(localise.DOWNLOAD_FOLDER)
        
    video_nodes = []
    images = []
    html = requests.get(page.url).content  # html is bytes; â‰¤/â‰¥ - 
    html = html.decode('utf-8') # force conversion to UTF-8 because lxml isn't.
    root = lxml.html.fromstring(html)
    article = root.xpath("//article[@id='article']")[0]
    videos = article.xpath("//iframe")
    for element in article.xpath("//div[@class='small related']"):
        element.drop_tree()
    for element in article.xpath("//div[@id='share']"):
        element.drop_tree()
    for video in videos:
        node, nodehash = get_video_node(video.attrib['src'])
        if nodehash: # skip if no filename because video probably broke
            # continue # skip video for now
            video_nodes.append(node)
            video.attrib['src'] = "/content/storage/{}/{}/{}".format(nodehash[0], nodehash[1], nodehash)
            video.attrib['localise'] = "skip"
            video.attrib['controls'] = "True"
            video.tag = "video"
            
    article_out = lxml.html.tostring(article)
    article_decode = article_out.decode('utf-8')
    
    new_html = template.replace("{name}", page.name).replace("{article}", article_decode)
    local_soup = localise.make_local_html(BeautifulSoup(new_html, "html5lib"), page.url, makefolder)
    tex_html = local_soup.prettify()
    svg_html = tex_to_svg.html_to_svg(tex_html)


    with open(localise.DOWNLOAD_FOLDER+"/index.html", "wb") as f:
        f.write(svg_html)



    zip_name = localise.finalise_zip_file(page.url)
    zip_file = HTMLZipFile(zip_name)
    zip_node = HTML5AppNode(source_id=page.url, title=page.name, license=CC_BY_NC_ND,
                           copyright_holder='Mathplanet', files=[zip_file])
    return zip_node, video_nodes

with open("template.html") as f:
    template=f.read()

if __name__ == "__main__":
    sample_url = "https://www.mathplanet.com/education/pre-algebra/introducing-algebra/inequalities"
    handle_lesson(FakePage(sample_url))

