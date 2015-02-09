while read start_time end_time interval max_item max_pages type conf_file
do
    run_file=../uniform/run/start_urls.run.$type
    echo '#'$start_time' '$end_time' '$interval' '$max_item' '$max_pages' '$type' '$conf_file
    cat $run_file|egrep '^http'|while read url
    do
        echo $start_time' '$end_time' '$interval' '$max_item' '$max_pages' '$conf_file' '$url
    done
done
