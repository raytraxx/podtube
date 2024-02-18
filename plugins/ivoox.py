import re
from typing import List, Union

import dateparser
import httpx
import urllib.request
from parsel import Selector, SelectorList

from core.model import PodcastFeed, PodcastItem
from core.options import Options
from core.scrape_utils import clean
from core.plugin.plugin import Plugin

import xml.etree.ElementTree as ET

import os


class PluginImpl(Plugin):
    class PluginOptions(Options):
        max_pagination: int = 1

    options: PluginOptions

    def get_feed(self, original_feed_id):
        """Calculates and returns the subscribable feed."""
        feed_id = original_feed_id.split("_")[-2]
        original_feed_url = f'https://www.ivoox.com/feed_fg_{feed_id}_filtro_1.xml'

        with urllib.request.urlopen(original_feed_url) as response:
            xml_contents = response.read()

        tree = ET.fromstring(xml_contents)
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

        host_url = os.environ.get("HOST_URL")
        if host_url:
            feed_url = f'{host_url}feed?service=ivoox&id={original_feed_id}'

            link_tag = tree.find("channel").find("atom:link", namespaces)
            link_tag.set("href", feed_url)

        for item in tree.find("channel").findall("item"):
            link = item.find("link").text
            item_id = "_".join(link.replace(".html", "").split("_")[-2:])
            url_tag = item.find("enclosure")
            url_tag.set("url", f"http://www.ivoox.com/liten_mn_{item_id}.mp3?internal=HTML5")

        return ET.tostring(tree, encoding="unicode")

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        match = re.match(r'.*(_\d+_\d)', item_id)
        podcast_id = match and match.group(1)[1:]
        return f'http://www.ivoox.com/listen_mn_{podcast_id}.m4a?internal=HTML5'
