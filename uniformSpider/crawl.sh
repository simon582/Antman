function test_valid()
{
    for url in `cat start_urls.test1`
    do
        valid=`echo $url |egrep -v "^#"|wc -l`
        if [ $valid -eq 0 ] ; then
            continue
        fi
        scrapy crawl uniform -a start_url=$url -a max_item=1 -a max_pages=1 1>out 2>err
        line=`grep 'main_xpath array len' err|head -n 1`
        elem_num=`echo $line|awk '{print $8}'`
        if [ "${elem_num}z" == "z" ] ; then
            echo 'failed to crawl '$url' elem_num is empty'
        elif [ $elem_num -eq 0 ] ; then
            echo 'failed to crawl '$url
        else
            echo 'success to crawl '$url' elem num '$elem_num
        fi
    done
}
function show_record()
{
    local start_url=$1
    local count=$2
    local table=$3
    scrapy crawl uniform -a start_url=$url -a max_item=10 -a max_pages=1 -a show_info=True 2>/dev/null > info.$count
    local display_name=`cat info.$count|awk -F"=" '/^display_name/{print $2}'`
    echo 'db.'$table'.findOne({"crawl_source": "'$display_name'"})'|mongo localhost:27017/content_db 
}
function remove_record()
{
    local start_url=$1
    local count=$2
    local table=$3
    scrapy crawl uniform -a start_url=$url -a max_item=10 -a max_pages=1 -a show_info=True 2>/dev/null > info.$count
    local display_name=`cat info.$count|awk -F"=" '/^display_name/{print $2}'`
    echo 'db.'$table'.remove({"crawl_source": "'$display_name'"})'|mongo localhost:27017/content_db &>/dev/null
}
function get_crawl_source()
{
    local start_url=$1
    local count=$2
    scrapy crawl uniform -a start_url=$url -a max_item=10 -a max_pages=1 -a show_info=True 2>/dev/null >info.$count
    local display_name=`cat info.$count|awk -F"=" '/^display_name/{print $2}'`
    echo $display_name
}
function run_many_site()
{
    local start_urls=$1
    local remove_old=$2
    local max_item=$3
    local max_pages=$4
    local table=$5
    echo $table > temp_table
    count=0
    for url in `cat $start_urls`
    do
        count=$((count+1))
        valid=`echo $url |egrep -v "^#"|wc -l`
        if [ $valid -eq 0 ] ; then
            continue
        fi
        #echo $count':start to swipe '$url
        local display_name=`get_crawl_source $url $count`        
        #echo 'db.info_temp.remove({'crawl_source':"'$display_name'"})'|mongo localhost:27017/content_db &>/dev/null
        echo $count':start to crawl '$url
        if [ $remove_old -eq 1 ] ; then
            remove_record $url $count $table
        fi
        scrapy crawl uniform -a start_url=$url -a max_item=$max_item -a max_pages=$max_pages -a temp_table=$table 1>out.$count 2>err.$count
        line=`grep 'main_xpath array len' err.$count|head -n 1`
        main_xpath_num=`echo $line|awk '{print $8}'`
        elem_num=`grep "'id': " err.$count |wc -l`
        if [ "${elem_num}z" == "z" ] ; then
            echo $count':failed to crawl '$url' elem_num is empty main_xpath_num '$main_xpath_num
        elif [ $elem_num -eq 0 ] ; then
            echo $count':failed to crawl '$url' main_xpath_num '$main_xpath_num
        else
            echo $count':success to crawl '$url' elem num '$elem_num' main_xpath_num '$main_xpath_num
            show_record $url $count $table
        fi
    done
    rm temp_table
}
function calculate()
{
    local start_urls=$1
    local table=$2
    count=0
    for url in `cat $start_urls`
    do
        count=$((count+1))
        valid=`echo $url |egrep -v "^#"|wc -l`
        if [ $valid -eq 0 ] ; then
            continue
        fi
        local display_name=`get_crawl_source $url $count`
        num=`echo 'db.'$table'.count({"crawl_source":"'$display_name'"})'|mongo localhost:27017/content_db|egrep -v '^MongoDB|^connecting|^bye'`
        echo 'start_url '$url' display_name '$display_name' '$num
        echo 'db.'$table'.findOne({"crawl_source":"'$display_name'"})'|mongo localhost:27017/content_db|egrep -v '^MongoDB|^connecting|^bye'
    done
}
function usage()
{
    local argv0=$1
    echo $argv0' test_valid'
    echo $argv0' run start_urls remove=0/1 max_item=100 max_pages=1 table=info_temp'
    echo $argv0' calculate'
}
if [ $# -lt 1 ] ; then
    usage $0
    exit -1
fi
if [ $1 == 'test_valid' ] ; then
    #run_many_site start_urls.test3 1 10 1 info_temp2
    run_many_site start_urls.test1 1 10 1 info_temp2
elif [ $1 == 'run' ] ; then
    #run_many_site start_urls.goods 0 100 1 info_temp
    run_many_site $2 $3 $4 $5 $6
elif [ $1 == 'calculate' ] ; then
    calculate start_urls.test4 info
else
    usage $0
    exit -1
fi
