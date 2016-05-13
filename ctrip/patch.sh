mkdir patch_log
nohup python patch.py 0 > patch_log/0.log &
for i in $(seq 39)
do
    echo $i
    nohup python patch.py $i > patch_log/$i.log &
done
