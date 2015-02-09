#!/bin/bash
function log_info()
{
    local info=$@
    date_str=`date +"%Y-%m-%d %H:%M:%S"`
    echo $date_str" "$info
}
function parse_line()
{
    local cmd_file=$1
    echo $cmd_file
    cat $cmd_file | while read minites command
    do
        while true;
        do
            echo $command > ${cmd_file}.command
            log_info 'start '$command' ... '
            local start_time=`date +"%s"`
            bash ${cmd_file}.command
            local end_time=`date +"%s"`
            local use_sec=$((end_time-start_time))
            log_info 'end use '$use_sec' sec '$command
            seconds=$((minites*60))
            log_info 'start to sleep after run '$command' ... '
            sleep $seconds
            log_info 'end to sleep after run '$command
        done
    done
}
parse_line $@
