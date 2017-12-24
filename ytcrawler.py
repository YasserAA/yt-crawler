from bs4 import BeautifulSoup
import re
import pprint
from saver import Saver

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

pp = pprint.PrettyPrinter(indent=4)


class YtCrawler(object):
    # Check the url
    def __init__(self, url):
        if 'youtube.com' not in url:
            raise ValueError("""Invalid link, only youtube links allowed. eg:\n
                playlist: 'https://www.youtube.com/watch?v=DXjpb7SFi3s&list=PLvFsG9gYFxY_2tiOKgs7b2lSjMwR89ECb'\n
                channel: 'https://www.youtube.com/user/AsapSCIENCE/videos'\n""")

        if 'list' in url:
            self.kind = 'playlist'
        elif 'user' in url:
            self.kind = 'channel'
        else:
            raise ValueError('Invalid youtube link.')
        self.url = url
        self.videos = {}

    # Connect to PhantomJs driver
    def __enter__(self):
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:8910',
                                       desired_capabilities=DesiredCapabilities.PHANTOMJS)
        return self

    # Disconnect from PhantomJs driver
    def __exit__(self, type, value, traceback):
        if self.driver:
            self.driver.quit()

    # Fetch a url and return a soup
    def get(self, url):
        self.driver.get(url)
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, 'lxml')

    # Fetch data and select the container of videos
    def fetch(self):
        print "Fetching Data ... "
        soup = self.get(self.url)
        self.saveHTML(soup)

        if self.kind == 'playlist':
            video_container_selector = '.playlist-videos-container .yt-uix-scroller-scroll-unit'
        else:
            video_container_selector = '.channels-content-item'

        self.video_containers = soup.select(video_container_selector)

    # Save fetched HTML (for testing purposes)
    def saveHTML(self, soup):
        html = soup.prettify().encode('utf-8')
        with open(self.kind + '.html', 'w') as page:
            page.write(html)

    # Parse video container and extract the data
    def parse(self):
        print "Parsing Data ..."
        for video_container in self.video_containers:
            self.video_container = video_container
            (video_name, video_url, video_id) = self.get_video()
            try:
                video_data = self.videos[video_id]
            except KeyError:
                self.videos[video_id] = {
                    'name': video_name,
                    'video_url': video_url,
                }
                video_data = self.videos[video_id]

            #  Fetches the the video page because the rest of the data are not available in the playlist
            if self.kind == 'playlist':
                self.video_container = self.get("https://www.youtube.com/" + video_url)

            video_data['thumb_link'] = self.get_thumb_link()
            video_data['duration'] = self.get_duration()
            video_data['views'] = self.get_views()
            video_data['full_thumb_link'] = self.get_full_thumb_url(video_id)

    # Get video title, url, and ID
    def get_video(self):
        if self.kind == 'playlist':
            link = self.video_container.select('a.playlist-video.yt-uix-sessionlink')[0]
            video_name = link.select('.yt-ui-ellipsis.yt-ui-ellipsis-2')[0].text
            video_url = link.get('href').split('&')[0]

        else:
            link = self.video_container.select('a.yt-uix-tile-link.yt-uix-sessionlink')[0]
            video_name = link.text
            video_url = link.get('href')

        video_id = video_url.split('v=')[-1]

        video_url = video_url.strip()
        video_name = video_name.strip()
        return (video_name, video_url, video_id)

    # Get video duration in sec
    def get_duration(self):
        if self.kind == 'playlist':
            time_str = self.video_container.select('.ytp-time-duration')[0].text
        else:
            time_str = self.video_container.select('.video-time')[0].span.text

        time_str = map(lambda s: int(s), time_str.split(':'))
        if len(time_str) > 2:
            return time_str[0] * 3600 + time_str[1] * 60 + time_str[2]
        else:
            return time_str[0] * 60 + time_str[1]

    # Get video views
    def get_views(self):
        if self.kind == 'playlist':
            views = self.video_container.select('.watch-view-count')[0].text
        else:
            views = self.video_container.select('.yt-lockup-meta-info')[0].text
        views = re.findall('\d+', views)
        return int(''.join(views))

    # Get the normal thumb url
    def get_thumb_link(self):
        if self.kind == 'playlist':
            return self.video_container.select('.yt-thumb-clip img')[0].get('data-thumb')
        else:
            return self.video_container.select('.video-thumb img')[0].get('src')

    # Get the full size thumb url
    def get_full_thumb_url(self, video_id):
        return "http://img.youtube.com/vi/%s/maxresdefault.jpg" % video_id
