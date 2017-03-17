nohup python main_p_n_test.py > svmsan.txt 2>&1 &
wait
nohup python main_san.py 0 1 10 > svmsan.txt 2>&1 &
nohup python main_san_time.py 0 1 10 > svmdsan.txt 2>&1 &
wait
nohup python main_sn.py 0 1 10 > svmsn.txt 2>&1 &
