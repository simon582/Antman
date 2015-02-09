# Scrapy settings for uniform project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'uniform'

SPIDER_MODULES = ['uniform.spiders']
NEWSPIDER_MODULE = 'uniform.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'uniform (+http://www.yourdomain.com)'
ITEM_PIPELINES=['uniform.pipelines.UniformPipeline']
#mongodb set
MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'content_db'
#MONGODB_COLLECTION = 'infos'
MONGODB_COLLECTION = 'info'
MONGODB_TEMP_COLLECTION = 'info_temp'
MONGODB_UNIQ_KEY = 'id'
MONGODB_ITEM_ID_FIELD = '_id'
MONGODB_SAFE = True
CONCURRENT_REQUESTS = 1

#LOGGING
LOG_LEVEL = 'WARNING'
