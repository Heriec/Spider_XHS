import json
import logging

import requests

from db.db_util import Db
from logger.logger import logger
from xhs_utils.xhs_util import get_headers, get_params, js, check_cookies, get_note_data, handle_note_info, norm_str


class OneNote:
    def __init__(self, cookies=None):
        if cookies is None:
            self.cookies = check_cookies()
        else:
            self.cookies = cookies
        self.feed_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'
        self.detail_url = 'https://www.xiaohongshu.com/explore/'
        self.headers = get_headers()
        self.params = get_params()
        self.db = Db()

    # 单个视频
    def get_one_note_info(self, url):
        note_id = url.split('/')[-1]
        data = get_note_data(note_id)
        data = json.dumps(data, separators=(',', ':'))
        ret = js.call('get_xs', '/api/sns/web/v1/feed', data, self.cookies['a1'])
        self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
        response = requests.post(self.feed_url, headers=self.headers, cookies=self.cookies, data=data)
        res = response.json()
        try:
            data = res['data']['items'][0]
        except:
            logger.info(f'笔记 {note_id} 不允许查看')
            return
        note = handle_note_info(data)
        return note

    # cover 是否覆盖
    def save_one_note_info(self, url, categoryName, need_cover=False, info='', dir_path='datas'):
        try:
            note = self.get_one_note_info(url)
            nickname = norm_str(note.nickname)
            title = norm_str(note.title)
            note_type = note.note_type
            # 该分支只处理视频到数据库中
            if note_type == 'video':
                img_url = note.image_list[0]['info_list'][1]['url']
                # download_media(path, 'cover', img_url, 'image', '视频封面')
                video_url = note.video_addr
                # download_media(path, 'video', video_url, 'video')
                self.db.insert_data(note.note_id, img_url, video_url, note.title, note.desc,
                                    int(note.liked_count), int(note.collected_count), int(note.comment_count), int(note.share_count),
                                    note.upload_time, note.tag_list, note.ip_location,
                                    categoryName)
                logger.info(f'用户: {nickname}, {info}标题: {title} 笔记保存成功')
                logger.info('===================================================================')
            return note
        except:
            logger.info(f'笔记 {url} 保存失败')
            return

    def main(self, url_list):
        for url in url_list:
            try:
                self.save_one_note_info(url)
            except:
                logger.info(f'笔记 {url} 保存失败')
                continue


if __name__ == '__main__':
    one_note = OneNote()
    url_list = [
        'https://www.xiaohongshu.com/explore/64356527000000001303282b',
        # 'https://www.xiaohongshu.com/explore/63d625f8000000001d01042c',
        # 'https://www.xiaohongshu.com/explore/61ac8820000000002103a8aa',
        # 'https://www.xiaohongshu.com/explore/62d2699c000000001200f101',
        # 'https://www.xiaohongshu.com/explore/637f0938000000001f012d15',
    ]
    one_note.main(url_list)
