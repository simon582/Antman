#!/bin/bash
function parse_conf()
{
    local conf_file=$1
    local count=0
    egrep -v '^#' $conf_file|while read line
    do
        echo 'start to handle '$line
        echo $line >.${conf_file}.line.$count
        nohup bash loop_crawl_parse_line.sh .${conf_file}.line.$count >> loop_crawl.out 2>&1 &
        count=$((count+1))
        sleep 5
        echo 'end to handle'
    done
}

function usage()
{
    local argv0=$1
    echo $argv0' conf_file=loop_crawl.conf'
}
if [ $# -lt 1 ] ; then
    usage $0
    exit -1
fi
conf_file=$1
parse_conf $conf_file
