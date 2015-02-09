date_str=`date +"%Y-%m-%d %H:%M:00"`
file_date_str=`date +"%Y-%m-%d_%H:%M:00"`
echo '线上各站点抓取量统计'$date_str > .title
function usage()
{
    local argv0=$0
    echo $0' debug=1/0'
}
if [ $# -ne 1 ] ; then
    usage $0
    exit -1
fi
#bash show_table_info.sh show_site_num ../uniform/run/start_urls.run.online > .origin_content
#cat .origin_content | cut -b 21- > .content
cat ../comm_lib/cat2.txt |egrep '^002'|awk '{print $3"\t"$4}' > .cat
yesterday_str=`date -d yesterday +"%Y-%m-%d_%H"`
yesterday_file=`ls -tr |grep online2_crawl_sites|egrep $yesterday_str |tail -n 1`
python show_table_info.py show_site_num ../uniform/run/start_urls.run.online .cat $yesterday_file > .content
tongji='online2_crawl_sites_'$file_date_str.txt
cp .content $tongji
if [ $1 -eq 1 ] ; then
    python send_mail.py luoyan@maimiaotech.com 62717038 luoyan@maimiaotech.com .title $tongji
else
    python send_mail.py ops@maimiaotech.com maimiaoops2013 2c@maimiaotech.com .title $tongji
fi
