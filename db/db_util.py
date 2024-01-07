from datetime import datetime

import pymysql

from logger.logger import logger


class Db(object):
    def __init__(self):
        # 打开数据库连接
        self.db = pymysql.connect(host='47.96.114.93',
                                  port=3306,
                                  user='root',
                                  password='ffe7b71c16cdc5ac6164fa9e3a89748d',
                                  database='xhs_spider')

    def insert_data(self, note_id, img_url, video_url, title, desc, liked_count, collected_count, comment_count,
                    share_count,
                    upload_time, tag_list, ip_location,
                    type):
        cursor = self.db.cursor()
        sql = (
            "INSERT INTO xhs_video(note_id, img_url, video_url, title, `desc`, liked_count, collected_count, comment_count, share_count, upload_time, tag_list, ip_location, type)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        # 要插入的数据
        data = (note_id, img_url, video_url, title, desc, liked_count, collected_count, comment_count, share_count,
                datetime.fromtimestamp(upload_time / 1000), ' '.join(tag_list), ip_location, type)

        try:
            # 执行SQL语句
            cursor.execute(sql, data)
            # 提交到数据库执行
            self.db.commit()
            logger.info("插入成功")
        except Exception as e:
            # 如果发生错误则回滚
            self.db.rollback()
            logger.info("插入失败：", e)

    def getId(self, note_id):
        cursor = self.db.cursor()
        query = "SELECT id FROM xhs_video WHERE note_id = %s"

        cursor.execute(query, note_id)
        result = cursor.fetchone()
        cursor.close()
        return result

    def close(self):
        self.db.close()
