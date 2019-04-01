#!/usr/bin/env python
import os
import sys
sys.path.append(os.getcwd()) # Handle relative imports
import requests
from le_utils.constants import licenses
import logging
from indexer import index_root
from ricecooker.chefs import SushiChef
from ricecooker.classes.nodes import TopicNode
import detail


LOGGER = logging.getLogger()


class MathplanetChef(SushiChef):
    channel_info = {
        'CHANNEL_SOURCE_DOMAIN': 'www.mathplanet.org', # who is providing the content (e.g. learningequality.org)
        'CHANNEL_SOURCE_ID': 'mathplanet',         # channel's unique id
        'CHANNEL_TITLE': 'Mathplanet',
        'CHANNEL_LANGUAGE': 'en',                          # Use language codes from le_utils
        'CHANNEL_THUMBNAIL': 'https://github.com/learningequality/sushi-chef-mathplanet/raw/master/mathplanet.png',
        'CHANNEL_DESCRIPTION': 'Take our high school math courses in Pre-algebra, Algebra 1 & 2 and Geometry, and practice tests for the SAT and ACT. Since maths is the same all over the world, we welcome everybody to study math with us.',  # (optional) description of the channel (optional)
    }

    def construct_channel(self, **kwargs):
        channel = self.get_channel(**kwargs)

        for cat in index_root.get_children():
            cat_node = TopicNode("__"+str(cat._id), cat.name)
            channel.add_child(cat_node)
            for subcat in cat.get_children():
                subcat_node = TopicNode("__"+str(subcat._id), subcat.name)
                cat_node.add_child(subcat_node)
                for article in subcat.get_children():
                    print ("article: ", article.name)
                    article_node = TopicNode("__"+str(article._id), article.name)
                    subcat_node.add_child(article_node)
                    htmlnode, videonodes = detail.handle_lesson(article)
                    article_node.add_child(htmlnode)
                    for video in videonodes:
                        article_node.add_child(video)
                        return channel # outdent for real version


if __name__ == '__main__':
    """
    Set the environment var `CONTENT_CURATION_TOKEN` (or `KOLIBRI_STUDIO_TOKEN`)
    to your Kolibri Studio token, then call this script using:
        python souschef.py  -v --reset
    """
    mychef = MathplanetChef()
    if 'KOLIBRI_STUDIO_TOKEN' in os.environ:
        os.environ['CONTENT_CURATION_TOKEN'] = os.environ['KOLIBRI_STUDIO_TOKEN']
    mychef.main()
