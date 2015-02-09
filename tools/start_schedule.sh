nohup python watchlog.py >> ../log/spider.log &
nohup python spider_schedule_sort.py schedule.conf > /dev/null &
nohup python ../ui/manage.py runserver 0.0.0.0:3333 > /dev/null &
