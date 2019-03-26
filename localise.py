import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import os
import requests_cache
import codecs
import shutil
from mime import mime
import urllib3
urllib3.disable_warnings()
requests_cache.install_cache()

DOMAIN = "artsedge.kennedy-center.org"
LINK_ATTRIBUTES = ["src", "href"]
DOWNLOAD_FOLDER = "downloads"
sample_url = "https://artsedge.kennedy-center.org/educators/lessons/grade-9-12/Arthur_Miller_and_The_Crucible"

response = requests.get(sample_url)
soup = BeautifulSoup(response.content, "html5lib")

"""
TODO LIST:
fix local anchors (even if they don't appear local)
correctly mangle links beginning with ~ -- i.e. ones with no domain
"""

print ("_")

def make_links_absolute(soup, base_url):
    for r in get_resources(soup):
        for attr in LINK_ATTRIBUTES:
            old_url = r.attrs.get(attr, None)
            url = old_url
            if not url:
                continue
            url = url.strip()
            url = urljoin(base_url, url)
            #if url != old_url:
            #    print ("Rewrote {} to {}".format(old_url, url))
            r.attrs[attr] = url

def guess_extension(filename):
    if "." not in filename[-8:]: # arbitarily chosen
        return ""
    ext = "." + filename.split(".")[-1]
    if "/" in ext:
        return ""
    return ext

def ext_from_mime_type(mime_type):
    if mime_type not in mime:
        return ""
    return mime[mime_type][0]

def get_resources(soup):
    def is_valid_tag(tag):
        if not any(link in tag.attrs for link in LINK_ATTRIBUTES):
            return False
        # do not rewrite self-links
        href = tag.attrs.get("href")
        if href and href[0]== "#":
            return False
        return True

    resources = set()
    for attribute in LINK_ATTRIBUTES:
        l = soup.find_all(lambda tag: is_valid_tag(tag))
        resources.update(l)
    return resources


def make_local(soup, page_url):
    def full_url(url):
        if urlparse(url).scheme == "":
            url = urljoin("https://", url)
        if urlparse(url).netloc == "":
            return urljoin(page_url, url)
        else:
            return url

    def hashed_url(url):
        return hashlib.sha1(full_url(url).encode('utf-8')).hexdigest() + guess_extension(full_url(url))


    try:
        shutil.rmtree(DOWNLOAD_FOLDER)
    except:
        pass

    make_links_absolute(soup, page_url)
    resources = get_resources(soup)

    try:
        os.mkdir(DOWNLOAD_FOLDER)
    except FileExistsError:
        pass

    raw_url_list = [resource.attrs.get('href') or resource.attrs.get('src') for resource in resources if "mailto:"]
    url_list = [x for x in raw_url_list if not x.startswith("mailto:")]
    url_list = [full_url(url) for url in url_list]

    # replace URLs
    resource_filenames = {}

    # download content
    # todo: don't download offsite a's?

    for resource in resources:
        for attribute in LINK_ATTRIBUTES:
            attribute_value = full_url(resource.attrs.get(attribute))
            if attribute_value and attribute_value in url_list:
                if attribute_value.startswith("mailto"):
                    continue
                if resource.name == "a" and urlparse(attribute_value).netloc not in (DOMAIN, "", "www.kennedy-center.org"):
                    #print (urlparse(attribute_value).netloc)
                    # print ("rewriting non-local URL {} in {}".format(attribute_value, resource.name))
                    new_tag = soup.new_tag("span")
                    u = soup.new_tag("u")
                    u.insert(0, resource.text)
                    new_tag.insert(0, " (url:\xa0{})".format(resource.attrs['href']))
                    new_tag.insert(0, u)
                    resource.replaceWith(new_tag)  # TODO -- this might mess up the iteration?
                    continue

                else:
                    if attribute_value not in resource_filenames:
                        try:
                            r = requests.get(attribute_value, verify=False)
                        except requests.exceptions.InvalidURL:
                            continue
                        content = r.content
                        try:
                            content_type = r.headers['Content-Type'].split(";")[0].strip()
                        except KeyError:
                            content_type = ""
                        extension = ext_from_mime_type(content_type)
                        filename = hashed_url(attribute_value)+extension

                        with open(DOWNLOAD_FOLDER+"/"+filename, "wb") as f:
                            try:
                                f.write(content)
                            except requests.exceptions.InvalidURL:
                                pass

                        resource_filenames[attribute_value] = filename

                    resource.attrs[attribute] = resource_filenames[attribute_value]
                    continue

    html = nice_html(soup)

    with codecs.open(DOWNLOAD_FOLDER+"/index.html", "wb") as f:
        f.write(html)
        
    # add modified CSS file
    os.mkdir(DOWNLOAD_FOLDER+"/resources")
    shutil.copy("main.css", DOWNLOAD_FOLDER+"/resources")

    # create zip file
    zipfile_name = shutil.make_archive("__"+DOWNLOAD_FOLDER+"/"+hashed_url(page_url), "zip", # automatically adds .zip extension!
                        DOWNLOAD_FOLDER)

    # delete contents of downloadfolder
    assert "downloads" in DOWNLOAD_FOLDER
    shutil.rmtree(DOWNLOAD_FOLDER)
    print(os.path.getsize(zipfile_name))
    

    return zipfile_name


def nice_html(soup):
    # TODO: download urls, mangle p.printTabHeadline to h2, mangle urls
    prefix = b"""
    <html>
    <head>
      <link rel="stylesheet" type="text/css" href="resources/main.css">
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    </head>
    <body>
      <div class="main">
      <div class="wrap">
      <div class="content">
    """

    suffix = b"""
    </div></div></div>
    </body>
    </html>"""



    output = []
    output.append(prefix)
    for tab in soup.find_all("div", {'class': 'tabscontent'}):
        output.append(str(tab).encode('utf-8'))
    output.append(suffix)
    return b"\n\n<!-- dragon -->\n\n".join(output)


if __name__ == "__main__":
    print (make_local(soup, sample_url))
