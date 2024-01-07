import json
import re
import time

import requests

from db.db_util import Db
from logger.logger import logger
from one import OneNote
from xhs_utils.xhs_util import get_headers, get_search_data, get_params, js, check_cookies


class Search:
    def __init__(self, cookies=None):
        if cookies is None:
            self.cookies = check_cookies()
        else:
            self.cookies = cookies
        self.search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
        self.headers = get_headers()
        self.params = get_params()
        self.oneNote = OneNote(self.cookies)
        self.db = Db()

    def get_search_note(self, query, number):
        data = get_search_data()
        api = '/api/sns/web/v1/search/notes'
        data = json.dumps(data, separators=(',', ':'))
        data = re.sub(r'"keyword":".*?"', f'"keyword":"{query}"', data)
        page = 0
        note_ids = []
        while len(note_ids) < number:
            page += 1
            data = re.sub(r'"page":".*?"', f'"page":"{page}"', data)
            ret = js.call('get_xs', api, data, self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.post(self.search_url, headers=self.headers, cookies=self.cookies,
                                     data=data.encode('utf-8'))
            res = response.json()
            if not res['data']['has_more']:
                logger.info(f'搜索结果数量为 {len(note_ids)}, 不足 {number}')
                break
            items = res['data']['items']
            for note in items:
                note_id = note['id']
                note_ids.append(note_id)
                if len(note_ids) >= number:
                    break
        return note_ids

    def handle_note_info(self, query, number, sort, categoryName, need_cover=False):
        data = get_search_data()
        data['sort'] = sort
        api = '/api/sns/web/v1/search/notes'
        data = json.dumps(data, separators=(',', ':'))
        data = re.sub(r'"keyword":".*?"', f'"keyword":"{query}"', data)
        page = 0
        index = 0
        while index < number:
            page += 1
            data = re.sub(r'"page":".*?"', f'"page":"{page}"', data)
            ret = js.call('get_xs', api, data, self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.post(self.search_url, headers=self.headers, cookies=self.cookies,
                                     data=data.encode('utf-8'))
            res = response.json()
            try:
                items = res['data']['items']
            except:
                logger.info(f'搜索结果数量为 {index}, 不足 {number}')
                break
            for note in items:
                index += 1
                # 去重
                if not self.db.getId(note['id']):
                    self.oneNote.save_one_note_info(self.oneNote.detail_url + note['id'], categoryName, need_cover, '',
                                                    'datas_search')
                else:
                    logger.info(note['id'] + "已存在")
                if index >= number:
                    break
            if not res['data']['has_more'] and index < number:
                logger.info(f'搜索结果数量为 {index}, 不足 {number}')
                break
        logger.info(f'搜索结果全部下载完成，共 {index} 个笔记')

    def main(self, info, categoryName):
        query = info['query']
        number = info['number']
        sort = info['sort']
        self.handle_note_info(query, number, sort, categoryName, need_cover=True)


if __name__ == '__main__':
    search = Search()
    # 搜索的关键词 
    query = '游戏'
    # 搜索的数量（前多少个）
    number = 2222
    # 排序方式 general: 综合排序 popularity_descending: 热门排序 time_descending: 最新排序
    sort = 'general'

    searchs = [
        {
            "categoryId": 4,
            "categoryName": "娱乐",
            "word": ["电影", "电视剧", "综艺节目", "话剧", "音乐剧", "明星娱乐", "演唱会", "舞台剧"]
        },
        {
            "categoryId": 5,
            "categoryName": "音乐",
            "word": ["流行音乐", "古典音乐", "摇滚乐", "爵士乐", "民谣", "电子音乐", "嘻哈音乐", "R&B"]
        },
        {
            "categoryId": 6,
            "categoryName": "二次元",
            "word": ["动漫", "漫画", "游戏原作", "二次元周边", "声优", "二次元活动", "虚拟偶像", "Cosplay"]
        },
        {
            "categoryId": 7,
            "categoryName": "美食",
            "word": ["中餐", "西餐", "日料", "韩料", "甜点", "烧烤", "火锅", "美食文化"]
        }
    ]
    for cs in searchs:
        for word in cs["word"]:
            info = {
                'query': word,
                'number': number,
                'sort': sort,
            }
            search.main(info, cs['categoryName'])
            time.sleep(60)
            logger.info('休眠60s' + cs['categoryName'])
        time.sleep(1800)
        logger.info('休眠1800s' + cs["categoryName"])
    logger.info('所有数据已完成！！！！')
