import feedparser
import subprocess

rss_urls = [ "https://tech.meituan.com/feed/" ]

for rss_url in rss_urls:
    feed = feedparser.parse( rss_url )
    items = feed["items"]
    for item in items:
        # print(item)
        time = item[ "published_parsed" ]
        title = item[ "title" ]
        link = item["link"]
        subprocess.call(["wget", link], shell=False)
        fileName = str(time.tm_year) + '-' + str(time.tm_mon) + '-' + str(time.tm_mday) + '-' + title + '.md'
        fileName = fileName.replace('/', '')
        f = open(fileName,'w')
        value = item["content"][0]['value']
        f.write('---\nlayout: post\ntitle: ' + title + '\n')
        f.write('''status: publish
published: true
meta:
  _edit_last: "1"
type: post
tags:
---
''')
        f.write(value)
    print('end ' + rss_url)

