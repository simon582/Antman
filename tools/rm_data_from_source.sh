function rm_data_from_source()
{
    local table=$1
    local source=$2
    echo 'remove data from source: '.$source.' in table '.$table
    echo 'db.'$table'.remove({"crawl_source":"'$source'"})'|mongo localhost:27017/content_db
}

function count_data_from_source()
{
    local table=$1
    local source=$2
    echo 'count data from source: '.$source.' in table '.$table
    echo 'db.'$table'.count({"crawl_source":"'$source'"})'|mongo localhost:27017/content_db|egrep -v 'Mongo|bye|connect'
}

function usage()
{
    local argv0=$1
    echo $argv0' rm/count daogou/news table_name'
}

function rm_crawl_source()
{
    echo 'Hello'
    local table=$1
    local rm=$2
    local name_list=$3
    for source in "${name_list[@]}" ; do
        echo 'source '$source
        if [ $rm -eq 1 ] ; then
            rm_data_from_source $table $source
        else:
            count_data_from_source $table $source
        fi
    done
}
function rm_daogou()
{
    local table=$1
    local rm=$2 
    for source in ${daogou_list[*]} ; do
        echo 'source '$source
        if [ $rm -eq 1 ] ; then
            rm_data_from_source $table $source
        else
            count_data_from_source $table $source
        fi
    done
}
function rm_news()
{
    local table=$1
    local rm=$2 
    for source in ${news_list[*]} ; do
        echo 'source '$source
        if [ $rm -eq 1 ] ; then
            rm_data_from_source $table $source
        else
            count_data_from_source $table $source
        fi
    done
}

declare -a daogou_list=('留住你' '什么值得买' '91特惠' '天上掉馅饼' '淘者' '发现值得买' '便宜多' '超值分享汇' '买什么便宜' '趣购365' '我爱白菜网' '我爱我的淘' '淘点便宜货' '每天优惠多' '买个便宜货' '什么值得淘' '360值得买' '淘宝特色' '360特惠' 'B5M值得买' '乐买网' '各种好吃的')

declare -a news_list=(
'百思不得姐'
'暴走漫画'
'内涵吧'
'糗事百科'
'囧事百科'
'杭州19楼'
'onlylady'
'太平洋女性网'
'汽车之家'
'三联生活周刊-封面故事'
'三联生活周刊-阅读'
'三联生活周刊-燃'
'三联生活周刊-美食'
'网易新闻'
'新浪新闻'
'凤凰网'
'腾讯新闻'
)
if [ $# -lt 2 ] ; then
    usage $0
    exit -1
fi
if [ $1 == 'rm' ] ; then
    echo 'Hi'
    rm_$2 $3 1 
elif [ $1 == 'count' ] ; then
    echo 'Hi'
    rm_$2 $3 0
fi

