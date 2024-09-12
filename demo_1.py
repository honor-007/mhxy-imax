import kmNet

from assets.sources import system_setting
from script_utils.loggerConfig import logger

def initKmNet():
    result = kmNet.init(system_setting['IP'], system_setting['Port'], system_setting['UUID'])
    if result == 0:
        logger.info("kmbox init success")
    else:
        logger.error("kmbox init fail")
