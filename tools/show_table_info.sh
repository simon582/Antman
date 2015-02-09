#!/bin/bash
date_str=`date +"%Y-%m-%d %H:%M:%S"`
function run_command()
{
    local db=$1
    local cmd=$2
    echo "================== cmd "$cmd" ================================="
    echo $cmd|mongo localhost:27017/$db|egrep -v "MongoDB|connecting|bye"
}
function get_sum()
{
    local sum=0
    while read n
    do
        sum=$((sum+n))
    done
    echo $sum
}
function log_info()
{
    local info=$@
    echo $date_str" "$info
}
function get_crawl_source()
{
    local start_url=$1
    local count=$2
    scrapy crawl uniform -a start_url=$start_url -a max_item=10 -a max_pages=1 -a show_info=True 2>/dev/null >info.$count
    local display_name=`cat info.$count|awk -F"=" '/^display_name/{print $2}'`
    echo $display_name
}
function get_mongodb_output()
{
    local db=$1
    shift 1
    local cmd=$@
    echo $cmd|mongo localhost:27017/$db|egrep -v '^MongoDB|^connecting|^bye'
}
function count_table()
{
    local db=$1
    local table=$2
    local count=`get_mongodb_output $db "db.$table.count()"`
    log_info $db' '$table' '$count
}

function show_one_record()
{
    local show_one=$1
    local table=$2
    local display_name=$3
    if [ $show_one -eq 0 ] ; then
        get_mongodb_output content_db 'db.'$table'.findOne({"crawl_source":"'$display_name'"})' > /dev/null
    else
        get_mongodb_output content_db 'db.'$table'.findOne({"crawl_source":"'$display_name'"})'
    fi
}
function show_cat_num()
{
    local table=$1
    local count=0
    sum=0
    cat ../comm_lib/cat2.txt |egrep '^002'|awk '{print $3"\t"$4}' > .cat
    while read cat_id cat_name
    do
        #echo 'db.'$table'.count({"cat":"'$cat_id'"})'
        count=`get_mongodb_output content_db 'db.'$table'.count({"cat":"'$cat_id'"})'`
        sum=$((sum+count))
        log_info "cat_name "$cat_name" "$count
    done < .cat
    log_info "total_cat_num 类别总量 "$sum
}
function show_site_num()
{
    local start_urls=$1
    local table=$2
    local show_one=$3
    cd ../uniform > /dev/null
    count_table content_db info
    count_table content_db info_temp
    count_table content_db info_weibo_temp
    count_table content_index info
    count=0
    chufang_num=0
    >.chufang
    for url in `cat $start_urls`
    do
        count=$((count+1))
        valid=`echo $url |egrep -v "^#"|wc -l`
        if [ $valid -eq 0 ] ; then
            continue
        fi
        local display_name=`get_crawl_source $url $count`
        local num=`get_mongodb_output content_db 'db.'$table'.count({"crawl_source":"'$display_name'"})'`
        local msg='crawl_num '$num' display_name '$display_name' start_url '$url
        log_info $msg
        total_msg=${total_msg}`log_info $msg`
        if [ $display_name == '厨房' ] ; then
            chufang_num=$num
            echo $chufang_num>.chufang
        fi
        show_one_record $show_one $table $display_name
    done > uniform.output
    chufang_num=`cat .chufang`
    for crawl_source in `cat ../tools/weibo_crawl_source`
    do
        local url='http://weibo.cn/search/mblog?hideSearchFrame=&keyword='
        local display_name=$crawl_source
        local num=`get_mongodb_output content_db 'db.'$table'.count({"crawl_source":"'$display_name'"})'`
        local msg='crawl_num '$num' display_name '$display_name' start_url '$url
        log_info $msg
        show_one_record $show_one $table $display_name
    done > weibo.output
    uniform_sum=`cat uniform.output|awk '{print $4}' | get_sum`
    uniform_sum=$((uniform_sum-chufang_num*2))
    weibo_sum=`cat uniform.output|awk '{print $4}' | get_sum`
    sum=$((uniform_sum+weibo_sum))
    total_sites=`cat uniform.output weibo.output|wc -l`
    uniform_sites=`cat uniform.output|wc -l`
    weibo_sites=`cat weibo.output|wc -l`
    valid_uniform_sites=`cat uniform.output|awk '{if ($4 != 0) print $0}'|wc -l`
    valid_weibo_sites=`cat weibo.output|awk '{if ($4 != 0) print $0}'|wc -l`
    online_num=`get_mongodb_output content_db 'db.info.count({"stat":1})'`
    offline_num=`get_mongodb_output content_db 'db.info.count({"stat":0})'`
    log_info "total_sum "$sum
    log_info 'uniform_sum '$uniform_sum
    log_info 'weibo_sum '$weibo_sum
    log_info 'total_sites '$total_sites
    log_info 'uniform_sites '$uniform_sites
    log_info 'valid_uniform_sites '$valid_uniform_sites
    log_info 'weibo_sites '$weibo_sites
    log_info 'valid_weibo_sites '$valid_weibo_sites
    log_info 'online_num '$online_num
    log_info 'offline_num '$offline_num
    cat uniform.output weibo.output
    cd - >/dev/null
    #echo 'db.
}
function usage()
{
    local argv0=$1
    echo $argv0' show_site_num start_url_file'
    echo $argv0' show_cat_num'
}
function show_total_cat_num()
{
    show_cat_num info > .cat_info
    show_cat_num info_old > .cat_info_old
    python tongji.py join .cat_info .cat_info_old 4 4 3 3 >.cat_info.today
    local date_str=`date -d yesterday +"%Y-%m-%d_%H"`
    local yesterday_file=`ls -tr |grep online_crawl_sites|egrep $date_str |tail -n 1`
    if [ "z"${yesterday_file} != "z" ] ; then
        egrep 'cat_name|total_cat_num' $yesterday_file >.cat_info.yesterday
        python tongji.py diff .cat_info.yesterday .cat_info.today 4 4 3 3
    else
        log_info "no yesterday_file for cat_name"
    fi
}
function show_total_site_num()
{
    local start_urls=$1
    show_site_num $start_urls info 0 > .site_info
    show_site_num $start_urls info_old 0 > .site_info_old
    egrep 'crawl_num' .site_info > .crawl_site_info
    egrep 'crawl_num' .site_info_old > .crawl_site_info_old
    python tongji.py join .crawl_site_info .crawl_site_info_old 3 3 5 5 >.crawl_site_info.today
    local yesterday_str=`date -d yesterday +"%Y-%m-%d_%H"`
    local yesterday_file=`ls -tr |grep online_crawl_sites|egrep $yesterday_str |tail -n 1`
    if [ "z"${yesterday_file} != "z" ] ; then
        egrep 'crawl_num' $yesterday_file >.crawl_site_info.yesterday.tmp
        while read line
        do
            log_info $line
        done<.crawl_site_info.yesterday.tmp > .crawl_site_info.yesterday
        python tongji.py diff .crawl_site_info.yesterday .crawl_site_info.today 3 3 5 7
    else
        log_info "no yesterday_file for crawl_num for "$yesterday_str
    fi
}

function show_job_list()
{
    count_table job_list pending
    count_table job_list running
    count_table job_list done
}
if [ $# -lt 1 ] ; then
    usage $0
    exit -1
fi
if [ $1 == 'show_site_num' ] ; then
    cd ../uniform > /dev/null
    show_site_num $2 info 0
    cd - >/dev/null
elif [ $1 == 'show_old_site_num' ] ; then
    cd ../uniform > /dev/null
    show_site_num $2 info_old 0
    cd - >/dev/null
elif [ $1 == 'show_site_info' ] ; then
    cd ../uniform > /dev/null
    show_site_num $2 info 1
    cd - > /dev/null
elif [ $1 == 'show_cat_num' ] ; then
    show_cat_num info
elif [ $1 == 'show_old_cat_num' ] ; then
    show_cat_num info_old
elif [ $1 == 'show_total_cat_num' ] ; then
    show_total_cat_num
elif [ $1 == 'show_total_site_num' ] ; then
    show_total_site_num $2
elif [ $1 == 'show_job_list' ] ; then
    show_job_list
else
    usage $0
    exit -1
fi
