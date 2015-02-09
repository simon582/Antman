total_block=10
function log_info()
{
    local info=$@
    local date_str=`date +"%Y-%m-%d %H:%M:%S"`
    echo $date_str" "$info
}
for i in `seq 1 $total_block`
do
    nohup python transform.py content_db info_temp content_db info run 0 0 $total_block $i>> ../log/transform.out.$i 2>> ../log/transform.err.$i &
done
while true;
do
    process_num=`ps aux|grep 'python transform.py content_db info_temp content_db info run'|grep -v grep|wc -l`
    if [ $process_num -gt 0 ] ; then
        log_info "wait for "$process_num" python transform.py process ..." 
        sleep 5
    else
        break
    fi
done
