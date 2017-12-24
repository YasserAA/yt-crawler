# -*- coding: utf-8 -*-
from saver import Saver
from ytcrawler import YtCrawler
import sys


if __name__ == "__main__":
    # Example links
    playlist = "https://www.youtube.com/watch?v=DXjpb7SFi3s&list=PLvFsG9gYFxY_2tiOKgs7b2lSjMwR89ECb"
    channel = "https://www.youtube.com/user/AsapSCIENCE/videos"

    # Get user link
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = channel

    # Connects to the mysql server
    with Saver() as saver:
        # Connects to the browser driver
        with YtCrawler(url) as yt_crawler:
            while(1):
                print "\n"
                yt_crawler.fetch()
                yt_crawler.parse()
                print "Found %s videos" % len(yt_crawler.videos)
                saver.save(yt_crawler.videos)
