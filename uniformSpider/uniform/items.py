#coding=utf-8
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class UniformItem(Item):
    # define the fields for your item here like:
    # name = Field()
    id = Field()                #item id
    crawl_source = Field()      #抓取内容
    crawl_url = Field()         #抓取内容URL
    title = Field()             #内容标题，如果是微博，有可能为空
    flush = Field()             #飘红字段列表
    desc = Field()              #列表描述，对于商品，如果有多项描述，只保存第一项。如果有desc，一定有text
    crawl_desc_img = Field()    #列表页图片
    desc_img = Field()          #列表页图片for app，经过转换
    crawl_text = Field()        #正文/正文图片
    text = Field()              #正文图片 for app，经过转换
    crawl_go_link = Field()     #原始商品链接（由推荐引擎最终封装为展示格式）
    go_link = Field()           #处理后的商品链接
    source_price = Field()      #原商品价格
    cur_price = Field()         #当前商品价格
    pub_time = Field()          #抓取时间
    cat = Field()               #内容分类（n级别分类使用一个字段）
    duplicate = Field()         #内容重复列表
    score = Field()             #内容评分
    stat = Field()              #状态0:new 1:use 2:delete
    pre_pub_time = Field()      #预发布时间
    type = Field()              #网页类型（微博，新闻）
    crawl_location = Field()    #抓取地址
    #针对淘宝商品抓取新增字段
    good_id = Field()           #淘宝商品id
    old_price = Field()         #记录历史价格
    promotion = Field()         #促销类型
    express_status = Field()    #快递状态
    comment = Field()           #商品评价
    desc_score = Field()        #描述相符分
    desc_avg_score = Field()    #描述相符分与同行业平均
    service_score = Field()     #服务态度分
    service_avg_score = Field() #服务态度分与同行业平均
    deliver_score = Field()     #卖家发货速度分
    deliver_avg_score = Field() #卖家发货速度分与同行业平均
    refund_rate = Field()       #30天退款率
    refund_avg_rate = Field()   #30天退款率与同行业平均
    complain_rate = Field()     #30天投诉率
    complain_avg_rate = Field() #30天投诉率与同行业平均
    penalty_rate = Field()      #30天处罚数
    penalty_avg_rate = Field()  #30天处罚数与同行业平均
    #shikee
    sample_cnt = Field()
    apply_cnt = Field()
    quality_cnt = Field()
    obtain_cnt = Field()
    #amazon
    asin = Field()
    intro_list = Field()
    desc_text = Field()
    img = Field() 
