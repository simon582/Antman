function get_info()
{
    local start_url=$1
    echo $start_url > tmp.conf
    scrapy crawl uniform -a start_urls_file=tmp.conf -a show_info=True > tmp.info
    cat tmp.info |awk -F "=" '/xpath_file/{print $2}'
}

function gen_part_html()
{
    local start_url=$1
    echo $start_url > tmp.conf
    scrapy crawl uniform -a start_urls_file=tmp.conf -a gen_part_html=True -L DEBUG
    local part_html=`get_info $start_url`
    #vimdiff $part_html ${part_html}.bak
    #echo "vi $part_html"
}

function crawl_html()
{
    local start_url=$1
    echo $start_url > tmp.conf
    scrapy crawl uniform -a start_urls_file=tmp.conf -L DEBUG -a max_pages=2 -a max_item=10 > out 2>err
    vi err
}
function usage()
{
    local argv0=$0
    echo $argv0' get_info'
    echo $argv0' gen_part_html'
    echo $argv0' crawl_html'
}
if [ $# -ne 2 ] ; then
    usage $0
    exit -1
fi
if [ $1 == 'get_info' ] ; then
    get_info $2
elif [ $1 == 'gen_part_html' ] ; then
    gen_part_html $2
elif [ $1 == 'crawl_html' ] ; then
    crawl_html $2
else
    usage $0
fi
