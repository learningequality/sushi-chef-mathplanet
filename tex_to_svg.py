# setup:
# install npm
# npm install mathjax-node-cli

import subprocess
import re
import lxml.html

def node_tex_svg(tex):
    # my node setup makes no sense -- you can probably delete cwd entirely in a sensible setup
    return subprocess.check_output(["node", "texsvg.js", tex], cwd="/home/dragon/chef/math")

def node_mml_svg(mml):
    # my node setup makes no sense -- you can probably delete cwd entirely in a sensible setup
    return subprocess.check_output(["node", "mmlsvg.js", mml], cwd="/home/dragon/chef/math")

def mmltosvg(html):
    root = lxml.html.fromstring(html)
    maths = root.xpath("//math")
    for math in maths:
        svg = node_mml_svg(lxml.html.tostring(math)) # TODO - kill contents of math
        math.insert(0, lxml.html.fromstring(svg))
    return lxml.html.tostring(root)
        
def textosvg(html):
    htmlbits = []
    dollardollars = list(re.finditer(r"(\$\$)", html))
    try:
        dollardollars.extend(list(re.search(r"(\()", html)))
    except TypeError:
        pass
    try:
        dollardollars.extend(list(re.search(r"(\))", html)))
    except TypeError:
        pass

    dollars = [1,2,3,4]
    starts = [dollardollars[d].end() for d in range(0,len(dollardollars),2)]
    ends = [ dollardollars[d].start() for d in range(1,len(dollardollars),2)]

    upto=0
    for s, e in zip(starts, ends):
        htmlbits.append(html[upto:s-2])
        fragment = (html[s:e])
        print (fragment)
        htmlbits.append(node_tex_svg(fragment).decode('utf-8'))
        upto=e+2

    htmlbits.append(html[upto:])
    return ''.join(htmlbits)

def html_to_svg(html):
    return mmltosvg(textosvg(html))

def html_to_svg_file(infile, outfile):
    with open(infile, "rb") as f:
        html=f.read().decode('utf-8')

    html = textosvg(html)  # some implicit utf-8 wrangling?
    html = mmltosvg(html)

    with open(outfile, "wb") as f:
        f.write(html)
        
if __name__ == "__main__":
    html_to_svg_file("demo.html", "demoout.html")
