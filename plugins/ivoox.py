import re
from typing import List

import dateparser
import requests
from parsel import Selector, SelectorList

from model import PodcastFeed, PodcastItem
from plugins.plugin import Plugin


class IvooxPlugin(Plugin):
    def get_feed(self, feed_id, base_url):
        """Calculates and returns the subscribable feed."""
        url = f'https://www.ivoox.com/{feed_id}.html'
        response = requests.get(url)
        sel = Selector(response.text)
        videos = sel.css('.modulo-type-episodio')
        return PodcastFeed(
            feed_id=feed_id,
            title=sel.css('#list_title_new::text').get(),
            description=sel.css('.overview::text').get(),
            link=url,
            image=sel.css("meta[property='og:image']::attr(content)").get(),
            items=self._get_items(videos, base_url)
        )

    def _get_items(self, items: SelectorList, base_url: str) -> List[PodcastItem]:
        return [self._get_item(item, base_url) for item in items]

    def _get_item(self, item: Selector, base_url: str) -> PodcastItem:
        url = item.css('.title-wrapper a::attr(href)').get()
        re_item_id = re.match(r'https?://www\.ivoox\.com/([-_\w\d]+)\.html', url)
        item_id = re_item_id and re_item_id.group(1)
        date = dateparser.parse(
            item.css('.action .date::attr(title)').get(),
            settings={'RETURN_AS_TIMEZONE_AWARE': True}
        )
        return PodcastItem(
            item_id=item_id,
            url=base_url + 'download?s=ivoox&id=' + item_id,
            title=item.css('.title-wrapper a::attr(title)').get(),
            description=item.css('.title-wrapper button::attr(data-content)').get() or '',
            date=date,
            image=item.css('a img::attr(data-src)').get(),
            content_type='audio/mp4',
        )

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        return self.extract_link(f'https://www.ivoox.com/{item_id}.html')

    def extract_link(self, url):
        """Calculates the downloadable url from the html url of an item."""
        re_item_id = re.match(r'https?://www\.ivoox\.com/.*(_\d+_\d)\.html', url)
        item_id = re_item_id and re_item_id.group(1)[1:]
        return f'http://www.ivoox.com/listen_mn_{item_id}.m4a?internal=HTML5'
