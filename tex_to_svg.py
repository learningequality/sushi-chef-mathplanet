# setup:
# install npm
# npm install mathjax-node-cli

import subprocess
import re
import lxml.html
from html import unescape

replacements = {"\C=2\pi r": "C=2\pi r",
                "\color{green} {-4\}\cdot \left (3x+y\right )=9\cdot {\color{green} {-4}": \
                    "\color{green} {-4}\cdot \left (3x+y\right )=9\cdot {\color{green} {-4}}",
                "\left\{\begin{matrix} 2y - 4x = 2 \\ y = -x + 4 \end{matrix}\right": \
                    "\left\{\begin{matrix} 2y - 4x = 2 \\ y = -x + 4 \end{matrix}\right.,
                "\m\angle A=\frac{1}{2}(m\overline{DE}-m\overline{BC} )": \
                    "\angle A=\frac{1}{2}(m\overline{DE}-m\overline{BC} )",
                }

def node_tex_svg(tex):
    # my node setup makes no sense -- you can probably delete cwd entirely in a sensible setup
    # the space is there to stop problems with "-|7" being interpreted as an option.
    if tex in replacements:
        tex = replacements[tex]
    svg = subprocess.check_output(["node", "texsvg.js", " "+tex], cwd="/home/dragon/chef/math")
    if not (svg.startswith(b"<svg")):
        with open("errorlog", "a") as f:
            f.write("\n***\n")
            f.write(tex)            
            f.write("\n***\n")
        raise
    assert (svg.startswith(b"<svg")):
    return svg    

def node_mml_svg(mml):
    # my node setup makes no sense -- you can probably delete cwd entirely in a sensible setup
    svg = subprocess.check_output(["node", "mmlsvg.js", mml], cwd="/home/dragon/chef/math")
    if not (svg.startswith(b"<svg")):
        with open("errorlog", "a") as f:

            f.write("\n***\n")
            f.write(tex)            
            f.write("\n***\n")
    assert (svg.startswith(b"<svg")):
    return svg

def mmltosvg(html):
    root = lxml.html.fromstring(html)
    maths = root.xpath("//math")
    for math in maths:
        svg = node_mml_svg(lxml.html.tostring(math))
        # remove contents of math
        for content in math.xpath("./*"):
            math.remove(content)
        math.tag="span"
        for attribute in math.keys():
            del (math.attrib[attribute])
        assert "xmlns" not in math.keys()
        math.insert(0, lxml.html.fromstring(svg))
    return lxml.html.tostring(root)  # TODO -- SVG BROKEN
        
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
        fragment = unescape((html[s:e]))
        htmlbits.append(node_tex_svg(fragment).decode('utf-8'))
        upto=e+2

    htmlbits.append(html[upto:])
    return ''.join(htmlbits)

def html_to_svg(html):
    return mmltosvg(textosvg(html))

def html_to_svg_file(infile, outfile):
    with open(infile, "rb") as f:
        html=f.read().decode('utf-8')

    html = textosvg(html)  
    html = mmltosvg(html)

    with open(outfile, "wb") as f:
        f.write(html)
        
if __name__ == "__main__":
    html_to_svg_file("demo.html", "demoout.html")
