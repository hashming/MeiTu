#!/usr/bin/env python

import requests
from pyquery import PyQuery as pq
import os
import logging
import time


logging.basicConfig(
    filename = 'run.log',
    filemode = 'w',
    datefmt = '%d-%m-%Y %H:%M%S',
    format = '%(asctime)s %(name)s: %(levelname)s: %(message)s',
    level = logging.INFO
)
logging.getLogger("requests").setLevel(logging.ERROR)


class Headers():

    @property
    def proxies(self):
        proxies = None
        url = 'http://127.0.0.1:8888/random'
        try:
            re = requests.get(url)
            if re.status_code == 200:
                proxy = re.text
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                proxies = {
                    "http": "http://" + proxy,
                    "https": "https://" + proxy,
                }
        except Exception as e:
            logging.exception(e)
        return proxies


    @property
    def headers(self):
        headers = {
            'authority': 'm.mzitu.com',
            'method': 'GET',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'Hm_lvt_dbc355aef238b6c32b43eacbbf161c3c=1568091179,1568091424; Hm_lpvt_dbc355aef238b6c32b43eacbbf161c3c=1568091451',
            'referer': 'https://www.mzitu.com/',  # 网址
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36',
        }
        return headers


def parse_group(html):
    if None == html or html == '':
        return None, None

    groups = []
    next_url = ''
    doc = pq(html)
    lis = doc('ul[id=pins] li').items()
    for li in lis:
        info = li('a')
        if info:
            group = {
                'link': info.attr.href,
                'name': info('img').attr.alt,
                'image': info('img').attr('data-original'),
            }
            groups.append(group)
    next_url = doc('[class="next page-numbers"]').attr.href
    return groups, next_url    

# 下载每组图片的整体信息
'''
 group = {
        'link': info.attr.href,
        'name': info.attr.alt,
        'image': info.attr.src,
    }
'''
def get_groups(url, max_page=1):
    groups = []
    group = []
    next_url = None
    count = 0
    
    headers = Headers()
    logging.info('开始更新组图库信息')
    while count < max_page:
        try:
            logging.info(url)
            req = requests.get(url=url, headers=headers.headers)
            if 200 == req.status_code:
                group, next_url = parse_group(req.text)
                if group:
                    groups += group
                if None == next_url:
                    logging.info('已经更新全部图库信息')
                    break
                else:
                    url = next_url
        except Exception as e:
            logging.exception(e)
        count += 1
    logging.info('组图库信息更新完成')
    return groups


def parse_image(url):
    if not url:
        return None, None
    
    link = ''
    next_url = ''
    headers = Headers()
    for i in range(5):
        try:
            res = requests.get(url, headers=headers.headers)
            if 200 == res.status_code:
                doc = pq(res.text)
                link = doc('.main-image a img').attr.src
                nexti = doc('.pagenavi a:last-child')
                next_url = nexti.attr.href if "下一页" in nexti.text() else None
                return link, next_url
        except Exception as e:
            if i == 4:
                logging.exception(e)
            else:
                logging.info('retry{}: {}'.format(i, e.args))
            time.sleep(i * 2)      
    return None, None

# 下载每组中的每张图片的信息
'''
image = {
    'name': "",
    'links': "",
}
'''

def get_images(groups):
    if [] == groups or groups == None:
        return None

    images = []
    logging.info('开始更新图库的图片信息')
    for group in groups:
        links = []
        image = {}
        image['name'] = group.get('name', None)
        url = group.get('link', None)
        logging.info('更新: {}'.format(image['name']))
        while url:
            logging.info(url)
            link, next_url = parse_image(url)
            if link:
                logging.info(link)
                links.append(link)
            if not next_url:
                break
            else:
                url = next_url
        image['links'] = links[:]
        images.append(image)
    logging.info('图库的图片信息更新完成')
    return images

def save_image(url=None, path='./'):
    if not url:
        return
    headers = Headers()
    filename = path + '/' + url.split('/')[-1]

    if os.path.exists(filename):
        return
    try:
        req = requests.get(url=url, headers=headers.headers)
        if 200 == req.status_code:
            with open(filename, 'wb') as f:
                f.write(req.content)
        else:
            logging.warning('response code: {}'.format(req.status_code))

    except Exception as e:
        logging.exception(e)
        time.sleep(1)
    

# 下载图片
def download_images(images):
    if not images:
        return

    logging.info('开始下载图片')
    for image in images:
        name = image.get('name', None)
        path = './image/' + name if name else './image/'
        if not os.path.exists(path):
            os.makedirs(path)
        
        logging.info('下载: {}'.format(name))
        urls = image.get('links', None)
        for url in urls:
            logging.info(url)
            save_image(url, path)
    logging.info('图片下载完成')
    return

def run():
    page_count = 2
    # url = 'https://www.mzitu.com/'
    url = 'https://www.mzitu.com/page/12/'
    groups = get_groups(url, page_count)
    images = get_images(groups)
    download_images(images)

if __name__ == '__main__':
    run()
    # save_image(url='https://i5.meizitu.net/2019/07/02a03.jpg')
