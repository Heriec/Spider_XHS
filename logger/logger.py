import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler(filename=r'log.log', mode='a', encoding='utf-8')])

logger = logging.getLogger()