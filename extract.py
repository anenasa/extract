import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "yt-dlp"))
import yt_dlp

class Extractor:
    def extract(self, url, option = {}):
        if url.startswith("https://hamivideo.hinet.net/") and url.endswith(".do"):
            url = self.extractHami(url, option)
        elif url == "https://news.ebc.net.tw/live":
            url = self.extractEBC(url)
        elif url.startswith("https://today.line.me/tw/v2/article/"):
            url = self.extractLine(url)
        elif url.startswith("https://embed.4gtv.tv/") or url.startswith("https://www.ftvnews.com.tw/live/live-video/1/"):
            url = self.extractFourgEmbed(url)

        ydl = yt_dlp.YoutubeDL(option)
        info_dict = ydl.extract_info(url, False)
        if 'url' in info_dict:
            return info_dict.get('url')
        else:
            return info_dict.get('entries')[0]['url']

    def extractHami(self, url, option = {}):
        id = url.split('/')[-1].split('.')[0]
        headers = option.get('http_headers')
        response = requests.get('https://hamivideo.hinet.net/api/play.do?freeProduct=1&id=' + id, headers=headers)
        j = response.json()
        return j['url']

    def extractEBC(self, url):
        response = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
        soup = BeautifulSoup(response.text, 'html.parser')
        el = soup.select_one('div#live-slider div.live-else-little-box')
        return el['data-code']

    def extractLine(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        el = soup.select_one('script:-soup-contains(__NUXT__)')
        script = el.text
        id = script.split('broadcastId:"')[1].split('"')[0]
        response2 = requests.get('https://today.line.me/webapi/glplive/broadcasts/' + id)
        j = response2.json()
        return j['hlsUrls']['abr']

    def extractFourgEmbed(self, url):
        if url.startswith("https://www.ftvnews.com.tw/live/live-video/1/"):
            id = url.split('/')[-1]
        else:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            el = soup.select_one('script:-soup-contains(ChannelId)')
            script = el.text
            id = script.split('ChannelId: "')[1].split('"')[0]
        response2 = requests.get('https://app.4gtv.tv/Data/GetChannelURL_Mozai.ashx?callback=channelname&Type=LIVE&ChannelId=' + id)
        return response2.text.split('VideoURL":"')[1].split('"')[0]
