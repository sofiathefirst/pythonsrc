
if [ ! -d "log/" ]; then 
mkdir log/
fi

 nohup python main_cnsnwight_roc_cmd.py 1 sep aa > log/aasep.txt 2>&1 &
 nohup python main_cnsnwight_roc_cmd.py 1 sep cn > log/aasep.txt 2>&1 &
 nohup python main_timesanwight_roc_cmd.py  > log/timelog.txt 2>&1 &
 wait
 nohup python main_randomwalk_sanwight_roc_cmd.py  0.93 10 > log/randomjulaug0.93_20.txt 2>&1 &
 wait
 python sanrwr_a.py &
  python snrwr_a.py &