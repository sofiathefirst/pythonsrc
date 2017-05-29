
# coding: UTF-8
import motor
import time
import base_serial
import periphery
import select
import sys
import os
import termios
import math
import mpu6050
#import mpu6050_head
import threading
import PID
#import uwb
import remote
import numpy as np  #矩阵运算模块
from datetime import datetime
import os, struct, array
from fcntl import ioctl
import JoystickModule as jm


#位置PID参数
Sp = 3
Si = 0
Sd = 0
#速度PID参数
Vp = 87.0
Vi = 1.4
Vd = 0
#加速度PID参数
Ap = 0.07
Ai = 0.004
Ad = 0

#侧向角速度PID
# YP = 1600
# YI = 0
# YD = 5
YP = 1600
YI = 0
YD = 0

#偏航角速度PID
# YawP = 5.6
# YawI = 0.3
# YawD = 0
YawP = 0.5
YawI = 0
YawD = 0

# 打印参数标志
print_flag = 0
move_or_param = 0
manual_back_flag = 0
stop_flag = 0

class TimerThread(threading.Thread):
    __dev = None
    __stopf = True

    print_end = 0
    mgoback = 0
    mgoback_oppsite =0

    # 偏摆电机限位
    runout_limited = 0

    # PID过程参数
    home_angle_goal = 0         #圆盘前进方向期望倾角(度)

    cur_time = 0
    last_time = 0
    cur_home_angle = 0
    cur_home_angle_filter = 0
    last_home_angle = 0
    last_home_angle_filter = 0
    cur_home_speed = 0
    cur_home_speed_filter = 0
    last_home_speed = 0
    last_home_speed_filter = 0
    cur_home_acc = 0
    cur_home_acc_filter = 0
    cur_home_acc_kalfilter = 0

    cur_Y_angle = 0    #侧向角速度

    H_33 = 1 #33号电机提供的正向的角动量
    H_35 = -1 #35号电机提供的负向的角动量
    H_Y = 0 #总的Y方向的角动量

    cur_runout_angle = 0
    cur_runout_angle2 = 0
    last_runout_angle = 0
    cur_runout_speed = 0

    runout_goback = 0

    up_flag = 0
    up_start_time = 0.0
    Vx = 0.0
    Sx = 0.0

    #卡尔曼滤波参数
    x_pred = 0
    x_post = 0
    v_pred = 0
    v_post = 0

    #中值滤波参数
    Num = 3                                                     #滤波参数
    angle_Index = 0                                             #索引号
    speed_Index = 0
    acc_Index = 0

    Judge_flag = 0                                              #滤波对象选择（1：angle 2：speed 3：acc）

    angle_datas = [0 for i in range(0,Num+1)]                   #原始数据
    speed_datas = [0 for i in range(0,Num+1)]
    acc_datas = [0 for i in range(0,Num+1)]

    angle_dataSamples = [0 for i in range(0,Num)]               #中间数据
    speed_dataSamples = [0 for i in range(0,Num)]
    acc_dataSamples = [0 for i in range(0,Num)]

    lowpass_filter_i = [0 for i in range(0,Num)]
    lowpass_filter_o = [0 for i in range(0,Num)]

    speed_run_17 = 0.0
    speed_run_18 = 0.0
    speed_run_19 = 0.0
    speed_run_20 = 0.0

    def __init__(self, device):
        threading.Thread.__init__(self)
        self.__dev = device

        self.positionPID = PID.PID(P = Sp, I = Si, D = Sd)          #位置PID调节
        self.speedPID = PID.PID(P = Vp, I = Vi, D = Vd)             #速度PID调节
        self.accPID = PID.PID(P = Ap, I = Ai, D = Ad)               #加速度PID调节
        self.YspeedPID = PID.PID(P = YP,I = YI,D = YD)    #侧向角速度PID调节
        self.YawspeedPID = PID.PID(P = YawP,I = YawI,D = YawD)    #偏航角速度PID调节


    def stop(self):
        self.__stopf = False

    def run(self):
        print "run start:"

        f=open('/home/ball_pid_15/'+time.strftime('%Y-%m-%d-%H-%M')+'.txt','w')#创建一个以时间命名的文件
        # print f
        # f.write(str("Sp=")+str(Sp)+'\r\n')
        # f.write(str("Si=")+str(Si)+'\r\n')
        # f.write(str("Sd=")+str(Sd)+'\r\n')
        # f.write(str("Vp=")+str(Vp)+'\r\n')
        # f.write(str("Vi=")+str(Vi)+'\r\n')
        # f.write(str("Vd=")+str(Vd)+'\r\n')
        # f.write(str("Ap=")+str(Ap)+'\r\n')
        # f.write(str("Ai=")+str(Ai)+'\r\n')
        # f.write(str("Ad=")+str(Ad)+'\r\n')
        # f.write(str("YawP=")+str(YawP)+'\r\n')
        # f.write(str("YawI=")+str(YawI)+'\r\n')
        # f.write(str("YawD=")+str(YawD)+'\r\n')
        # f.write(str("YP=")+str(YP)+'\r\n')
        # f.write(str("YI=")+str(YI)+'\r\n')
        # f.write(str("YD=")+str(YD)+'\r\n')
        home_angle = 0
        home_speed = 0
        home_acc = 0
        runout_speed_goal = 0
        runout_speed_goal2 = 0

        home_angle_init_cnt = 0
        home_angle_offset = 0.0

        while self.__dev['stand']['home'].angle_x == 0.0:
            pass
        while (home_angle_init_cnt < 200):
            home_angle = Attitude_plant(self.__dev['stand']['home'].angle_x/ 180.0 * 3.14159265358979, \
                                        self.__dev['stand']['home'].angle_y/ 180.0 * 3.14159265358979, \
                                        self.__dev['stand']['home'].angle_z/ 180.0 * 3.14159265358979)
            home_angle_offset += home_angle
            home_angle_init_cnt +=1
        else:
            home_angle_offset /= 200


        while self.__stopf:
            time.sleep(0.005)        #频率100Hz
            self.cur_time = time.time()

            # self.cur_runout_angle = self.__dev['stand']['runout'].angle_y                           # 实际偏摆角度，初始时飞轮偏摆角在-0.5°~0.5°以内，限位角度不超过38°
            self.cur_runout_angle2 = self.__dev['stand']['runout2'].angle_y
            self.cur_runout_angle = -self.cur_runout_angle2
            # self.cur_runout_speed = self.__dev['stand']['runout'].gyr_y * 60 / 360 * (71*85/35)     # 偏摆电机实际偏摆速度，单位（rpm）
            self.cur_runout_speed = -self.__dev['stand']['runout2'].gyr_y * 60 / 360 * (71*85/35)

            # 圆盘倾角解算
            home_angle = Attitude_plant(self.__dev['stand']['home'].angle_x/ 180.0 * 3.14159265358979, \
                self.__dev['stand']['home'].angle_y/ 180.0 * 3.14159265358979, \
                self.__dev['stand']['home'].angle_z/ 180.0 * 3.14159265358979)

            cur_Y_angle = Attitude_plant_roll(self.__dev['stand']['home'].angle_x/ 180.0 * 3.14159265358979, \
                self.__dev['stand']['home'].angle_y/ 180.0 * 3.14159265358979, \
                self.__dev['stand']['home'].angle_z/ 180.0 * 3.14159265358979)

            self.cur_home_angle = (home_angle - home_angle_offset) * 180 / 3.14159265358979  # 圆盘当前倾角改变量，单位转换为（°）
            if math.fabs(self.cur_home_angle) < 0.1:
                self.cur_home_angle = 0

            self.cur_home_speed = self.__dev['stand']['home'].gyr_x * 0.707106781 + self.__dev['stand']['home'].gyr_y * 0.707106781   # 圆盘当前倾角角速度，单位（°/s）

            print self.cur_home_angle, self.cur_home_speed, cur_Y_angle,'jhhhhhh'

            if 1:
                self.Judge_flag = 2
                self.median_filter(self.cur_home_speed)                                   #中值滤波
                # self.lowpass_filter_i.pop(0)                                                     #2阶低通滤波
                # self.lowpass_filter_i.append(self.cur_home_speed)
                # self.cur_home_speed_filter = 1.1429805*self.lowpass_filter_o[-1]-0.4128016*self.lowpass_filter_o[-2] \
                #     +0.06745527*self.lowpass_filter_i[-1]+0.13491055*self.lowpass_filter_i[-2]+0.06745527*self.lowpass_filter_i[-3]
                # self.lowpass_filter_o.pop(0)
                # self.lowpass_filter_o.append(self.cur_home_speed_filter)

            delta_time = self.cur_time - self.last_time
            delta_home_speed = self.cur_home_speed_filter - self.last_home_speed

            if delta_time > 0:
                self.cur_home_acc = delta_home_speed / delta_time                           #圆盘当前倾角的角加速度

            if 1:
                self.Judge_flag = 3
                self.median_filter(self.cur_home_acc)                                   #中值滤波
#                 self.cur_home_acc_kalfilter = self.kalman_filter(self.cur_home_acc_filter, delta_time)        #卡尔曼滤波

            # 记录数据
            self.last_time = self.cur_time
            self.last_home_speed = self.cur_home_speed_filter

            # 三环控制
            pos_error = self.home_angle_goal - self.cur_home_angle      #角度偏差
            #if math.fabs(pos_error) < 0.5:
            #    pos_error = 0


#             if math.fabs( self.cur_home_angle)<10:

#                 self.positionPID.update(pos_error)                          #位置环PID
#                 home_speed_goal = self.positionPID.output                   #期望角速度

#             # vel_error = 0* home_speed_goal - self.cur_home_speed           #角速度偏差
#                 vel_error = 0* home_speed_goal - self.cur_home_speed_filter      #角速度偏差
# #             if math.fabs(vel_error) < 0.5:
# #                 vel_error = 0

#                 self.speedPID.update(vel_error)                             #速度环PID
#                 home_acc_goal = self.speedPID.output                        #期望角加速度

#                 acc_error = home_acc_goal - self.cur_home_acc_filter
#                 self.accPID.update(acc_error)
#                 runout_speed_goal = self.accPID.output * 30 / 3.14159265358979   #输出偏摆角速度(单位改为rpm)
#             else:
#                 runout_speed_goal = -self.cur_home_angle/math.fabs(self.cur_home_angle) *3500
#                 
            self.positionPID.update(pos_error)                          #位置环PID
            home_speed_goal = self.positionPID.output                   #期望角速度
            vel_error = 0* home_speed_goal - self.cur_home_speed_filter      #角速度偏差
            self.speedPID.update(vel_error)                             #速度环PID
            home_acc_goal = self.speedPID.output                        #期望角加速度
            acc_error = home_acc_goal - self.cur_home_acc_filter
            self.accPID.update(acc_error)
            runout_speed_goal = self.accPID.output * 30 / 3.14159265358979   #输出偏摆角速度(单位改为rpm)

            runout_speed_goal = runout_speed_goal / math.cos(self.cur_runout_angle / 180 * 3.14159265358979)    # 加入偏摆角度对陀螺力矩的分解影响

            home_roll_speed = -self.__dev['stand']['home'].gyr_x * 0.707106781 + self.__dev['stand']['home'].gyr_y * 0.707106781
            #  侧向角速度PID代码
            Y_angle_err = 0 - cur_Y_angle
            self.YspeedPID.update(Y_angle_err)
            motor_speed_offset = self.YspeedPID.output   #侧向电机的输出补偿

            # if math.fabs(cur_Y_angle)*180 / 3.14159265358979 < 2:
            #     motor_speed_offset = 0

            # if cur_Y_angle * home_roll_speed < 0 and math.fabs(cur_Y_angle)*180 / 3.14159265358979 > 30:
            #     self.speed_run_17 = speed_run* power17 - motor_speed_offset*0.5  #17.18号麦轮加速
            #     self.speed_run_18 = speed_run* power18 + motor_speed_offset*0.5
            #     self.speed_run_19 = speed_run* power19 - motor_speed_offset*0.5  #19 20号麦轮减速
            #     self.speed_run_20 = speed_run* power20 + motor_speed_offset*0.5

            # # elif cur_Y_angle * home_roll_speed > 0:
            # else :
            #     self.speed_run_17 = speed_run* power17 + motor_speed_offset*3  #17.18号麦轮加速
            #     self.speed_run_18 = speed_run* power18 - motor_speed_offset*3
            #     self.speed_run_19 = speed_run* power19 + motor_speed_offset*3   #19 20号麦轮减速
            #     self.speed_run_20 = speed_run* power20 - motor_speed_offset*3

            # self.speed_run_17 = speed_run* power17 + motor_speed_offset  #17.18号麦轮加速
            # self.speed_run_18 = speed_run* power18 - motor_speed_offset
            # self.speed_run_19 = speed_run* power19 + motor_speed_offset  #19 20号麦轮减速
            # self.speed_run_20 = speed_run* power20 - motor_speed_offset


            if self.mgoback % 2 ==1 :
                runout_speed_goal += 500
                # self.mgoback += 1

            if self.mgoback_oppsite % 2 ==1 :
                runout_speed_goal -= 500
                # self.mgoback_oppsite += 1


            # 飞轮手动回中处理 manual_back_flag为手动回中标志字
            if manual_back_flag % 2 ==0 :
                runout_speed_goal2 = runout_speed_goal
            elif manual_back_flag % 2 ==1 :
                runout_speed_goal = -500 * (self.cur_runout_angle >= 1.0) + 500 * (self.cur_runout_angle <= -1.0) \
                - 10 * self.cur_runout_angle * ( math.fabs(self.cur_runout_angle) < 1.0)
                runout_speed_goal2 = 500 * (self.cur_runout_angle2 >= 1.0) - 500 * (self.cur_runout_angle2 <= -1.0) \
                + 10 * self.cur_runout_angle2 * ( math.fabs(self.cur_runout_angle2) < 1.0)

            # 偏摆电机自动回中，条件：1、期望偏摆速度 < 150rpm；2、角度偏差 < 1°；3、速度偏差 < 0.5°/s4、加速度偏差 < 0.2°/s^2
#           print "%.6f  %.6f  %.6f  %.6f  %.6f"%(runout_speed_goal,pos_error,vel_error,acc_error,self.cur_runout_angle)
#
            #if 1 and math.fabs(runout_speed_goal) < 150 and math.fabs(pos_error) < 1 and math.fabs(vel_error) < 1 and math.fabs(acc_error) < 10:
                #if math.fabs(self.cur_runout_angle) > 10:
                   # self.runout_goback = - 2.5 * self.cur_runout_angle * (math.fabs(self.cur_runout_angle) < 20) \
                   # - 50 * (self.cur_runout_angle >= 20) \
                   # + 50 * (self.cur_runout_angle <= -20)
               # elif math.fabs(self.cur_runout_angle) > 1.5:
                  #  self.runout_goback = -20 * (self.cur_runout_angle > 1.2) + 20 * (self.cur_runout_angle < -1.2)
              #  elif math.fabs(self.cur_runout_angle) < 0.8:            # 留下一个过渡区间，防止runout_goback跳变，会使铭朗驱动器保护
                  #  self.runout_goback = 0
           # else:
               # self.runout_goback = 0
           # runout_speed_goal += self.runout_goback                     # 偏摆回中反馈加入输出速度中
#             print "%.6f  %.6f "%(runout_speed_goal, -self.runout_goback)


            # home_roll_speed = -self.__dev['stand']['home'].gyr_x * 0.707106781 + self.__dev['stand']['home'].gyr_y * 0.707106781
            # # 偏摆电机加上圆盘滚转角速率，同向转动
            # runout_speed_goal = runout_speed_goal -home_roll_speed * 60 / 360 * (71*85/35)
            # runout_speed_goal2 = runout_speed_goal2 +home_roll_speed * 60 / 360 * (71*85/35)



            Yaw_speed_err = 0 - self.__dev['stand']['home'].gyr_z
            self.YawspeedPID.update(Yaw_speed_err)
            offset = self.YawspeedPID.output
            self.H_Y = self.H_33*math.sin(-self.cur_runout_angle / 180 * 3.14159265358979) + self.H_35*math.sin(-self.cur_runout_angle2 / 180 * 3.14159265358979)
            # print self.H_Y

            # if math.fabs(self.H_Y) > 0.1:
            #     runout_speed_goal = runout_speed_goal - (-offset)/self.H_Y * 60 / 360 * (71*85/35)
            #     runout_speed_goal2 = runout_speed_goal2 + (-offset)/self.H_Y * 60 / 360 * (71*85/35)
            # else :
            #     runout_speed_goal = runout_speed_goal
            #     runout_speed_goal2 = runout_speed_goal2

            # if math.fabs(self.H_Y) > 0.1:
            #     runout_speed_goal = (-offset)/self.H_Y * 60 / 360 * (71*85/35)
            #     runout_speed_goal2 = - (-offset)/self.H_Y * 60 / 360 * (71*85/35)
            # else :
            #     runout_speed_goal = 0
            #     runout_speed_goal2 = 0
            #     # print (-offset)/self.H_Y * 60 / 360 * (71*85/35)
            #
            #
            #
            #
            # runout_speed_goal = runout_speed_goal -offset * 60 / 360 * (71*85/35)
            # runout_speed_goal2 = runout_speed_goal2 +offset * 60 / 360 * (71*85/35)



            # 偏摆电机限位处理
            if 1 and math.fabs(self.cur_runout_angle) > 35:                              # 到达限位角
                if runout_speed_goal * self.cur_runout_angle > 0:           # 期望偏摆速度使偏摆角继续增加（超过限位）
                    runout_speed_goal = 0
                    runout_speed_goal2 = 0
                    self.positionPID.clear()
                    self.speedPID.clear()
                    self.accPID.clear()

            if 1 and math.fabs(self.cur_runout_angle2) > 35:                              # 到达限位角
                if runout_speed_goal2 * self.cur_runout_angle2 < 0:           # 期望偏摆速度使偏摆角继续增加（超过限位）
                    runout_speed_goal = 0
                    runout_speed_goal2 = 0
                    self.positionPID.clear()
                    self.speedPID.clear()
                    self.accPID.clear()

            # 限制偏摆电机转速
            if math.fabs(runout_speed_goal) < 15:                             #速度太小时，铭朗控制器会速度失控报错
                runout_speed_goal = 0
            if runout_speed_goal > 3500:
                runout_speed_goal = 3500
            elif runout_speed_goal < -3500:
                runout_speed_goal = -3500

            if math.fabs(runout_speed_goal2) < 15:                             #速度太小时，铭朗控制器会速度失控报错
                runout_speed_goal2 = 0
            if runout_speed_goal2 > 3500:
                runout_speed_goal2 = 3500
            elif runout_speed_goal2 < -3500:
                runout_speed_goal2 = -3500
            # 打印输出（由键盘数字‘3’进行切换）
            if print_flag % 2 == 1:
                # print "%.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %s  %s"%(self.cur_home_angle,self.cur_home_speed_filter,self.cur_home_acc,self.cur_home_acc_filter, \
                print "%.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %s  %s"%(self.cur_time,self.cur_home_angle,home_angle_offset,self.cur_runout_angle, \
                                                            self.cur_home_speed,self.cur_home_speed_filter,self.cur_home_acc,self.cur_home_acc_filter, \
                                                            home_speed_goal,vel_error,home_acc_goal,acc_error, \
                                                            runout_speed_goal,self.cur_runout_speed,self.cur_runout_angle,self.runout_goback,param_flag)
#                 print "%.6f  %.6f  %.6f"%(runout_speed_goal, self.cur_runout_speed, self.cur_runout_angle)
            elif (print_flag % 2 == 0) and (self.print_end % 2 == 1):
                print "%s  %s  %s  %s  %s  %s  %s  %s  %s      %s"%(Ap,Ai,Ad,Vp,Vi,Vd,Sp,Si,Sd,param_flag)
                self.print_end += 1
#                 print "%s  %s"%(self.cur_home_angle,home_angle_offset * 180 / 3.14159265358979)
#                 print "%s  %s  %s  %s"%(self.cur_home_speed,self.cur_home_acc,self.cur_home_acc_filter,self.cur_home_acc_kalfilter)
            #print "%d  %.6f  %.6f  %.6f  %.6f"%(manual_back_flag,self.cur_runout_angle,self.cur_runout_angle2,runout_speed_goal,runout_speed_goal2)
            #

            self.__dev['run']['motorw2'].set_speed(runout_speed_goal2)  #runout_speed_goal为正时，偏摆电机逆时针转动，飞轮作用为帮助圆盘抬头，此时偏摆mpu角度增加
            self.__dev['run']['motorw1'].set_speed(runout_speed_goal)

            # 偏航角速率的影响加入到麦轮上
            # Yaw_speed_err = 0 - self.__dev['stand']['home'].gyr_z
            # self.YawspeedPID.update(Yaw_speed_err)
            # offset = self.YawspeedPID.output

            # if power17*speed_run > 0:
            #     signFlag = 1
            # elif power17*speed_run < 0:
            #     signFlag = -1
            # else:
            #     signFlag = 0

            # self.speed_run_17 = speed_run + offset*signFlag  #17.18号麦轮加速
            # self.speed_run_18 = speed_run + offset*signFlag
            # self.speed_run_19 = speed_run - offset*signFlag  #19 20号麦轮减速
            # self.speed_run_20 = speed_run - offset*signFlag

            # self.speed_run_17 = speed_run + (offset*signFlag + motor_speed_offset)  #17.18号麦轮加速
            # self.speed_run_18 = speed_run + (offset*signFlag + motor_speed_offset)
            # self.speed_run_19 = speed_run - (offset*signFlag + motor_speed_offset)  #19 20号麦轮减速
            # self.speed_run_20 = speed_run - (offset*signFlag + motor_speed_offset)

            #写数据到文件中
            #f.write(str(self.cur_time))
             		# str(self.cur_home_angle),str(home_angle_offset),str(self.cur_runout_angle), \
            #         str(self.cur_home_speed),str(self.cur_home_speed_filter),str(self.cur_home_acc),str(self.cur_home_acc_filter), \
            #         str(home_speed_goal),str(home_acc_goal), str(runout_speed_goal),str(self.cur_runout_speed),\
            #         str(self.cur_runout_angle),str(self.runout_goback))
            #f.write('\r\n')

            # print '%.6f %.6f %.6f %.6f %.6f' %(delta_time,time.time()-self.cur_time,self.__dev['stand']['home'].gyr_x,self.__dev['stand']['home'].gyr_y,self.__dev['stand']['home'].gyr_z)
            # print self.__dev['stand']['runout'].gyr_x,self.__dev['stand']['runout'].gyr_y,self.__dev['stand']['runout'].gyr_z
            # print self.__dev['stand']['home'].gyr_x,self.__dev['stand']['home'].gyr_y,self.__dev['stand']['home'].gyr_z,self.__dev['stand']['home'].angle_x,self.__dev['stand']['home'].angle_y,self.__dev['stand']['home'].angle_z


            # ax,ay,az = acc_NED(self.__dev['stand']['home'].angle_x/ 180.0 * 3.14159265358979,self.__dev['stand']['home'].angle_y/ 180.0 * 3.14159265358979,self.__dev['stand']['home'].angle_z/ 180.0 * 3.14159265358979,\
            #     self.__dev['stand']['home'].acc_x,self.__dev['stand']['home'].acc_y,self.__dev['stand']['home'].acc_z)
            ax,ay,az = acc_NED(self.__dev['stand']['home'].angle_x/ 180.0 * 3.14159265358979,self.__dev['stand']['home'].angle_y/ 180.0 * 3.14159265358979,0,\
                self.__dev['stand']['home'].acc_x,self.__dev['stand']['home'].acc_y,self.__dev['stand']['home'].acc_z)   # 转化到与IMU相关的水平坐标系
            print>>f,'%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f' %(self.cur_time, -ax/math.sqrt(2)+ay/math.sqrt(2), ax/math.sqrt(2)+ay/math.sqrt(2), az, \
                self.__dev['stand']['home'].gyr_x, self.__dev['stand']['home'].gyr_y, self.__dev['stand']['home'].gyr_z, \
                self.__dev['stand']['home'].angle_x, self.__dev['stand']['home'].angle_y, self.__dev['stand']['home'].angle_z, \
                self.speed_run_17/100.0, \
                self.cur_home_angle, self.cur_home_speed)
            f.write('\r\n')

            if self.up_flag == 1:
                self.speed_run_17 = 3500*power17/0.707
                self.speed_run_18 = 3500*power18/0.707
                self.speed_run_19 = 3500*power19/0.707
                self.speed_run_20 = 3500*power20/0.707
                up_time = time.time()-self.up_start_time
                if up_time < 1.3:
                    self.Sx += self.Vx*delta_time + (-ax/math.sqrt(2)+ay/math.sqrt(2))*delta_time*delta_time/2
                    self.Vx += (-ax/math.sqrt(2)+ay/math.sqrt(2))*delta_time
                    if self.Sx >= 0.15:
                        print 'self.Sx = %f, up_time = %f, Go up stair Successfully!!' %(self.Sx, up_time)
                        self.speed_run_17 = 0
                        self.speed_run_18 = 0
                        self.speed_run_19 = 0
                        self.speed_run_20 = 0
                        self.up_flag = 0
                        self.Sx = 0.0
                        self.Vx = 0.0
                else:
                    print 'self.Sx = %f, up_time = %f, Go up stair Failed!!' %(self.Sx, up_time)
                    self.speed_run_17 = 0
                    self.speed_run_18 = 0
                    self.speed_run_19 = 0
                    self.speed_run_20 = 0
                    self.up_flag = 0
                    self.Sx = 0.0
                    self.Vx = 0.0
            else:
                self.speed_run_17 = 0
                self.speed_run_18 = 0
                self.speed_run_19 = 0
                self.speed_run_20 = 0
            # print self.__dev['stand']['home'].acc_z,az
    #一阶低通滤波

    # 卡尔曼滤波
    def kalman_filter(self,x_new,dt):
        self.x_pred = self.x_post + dt * self.v_pred
        self.v_pred = self.v_post

        error = x_new - self.x_pred

        self.x_post = self.x_pred + 0.3 * error
        self.v_post = self.v_pred + 1 * error
        return self.x_post

    # 中值滤波
    def median_filter(self,x_new):

        if self.Judge_flag == 1:
            self.angle_datas[self.angle_Index] = x_new                              #在数组末增加一个新数据
            if self.angle_Index < self.Num:
                self.angle_Index += 1
                self.cur_home_angle_filter = x_new
            else:                                                             #采集到Num+1个数据后开始滤波
                self.med_filter_update()
                if self.Num == 3:
                   self.quickMedianFilter3()
                elif self.Num == 5:
                    self.quickMedianFilter5()
                elif self.Num == 7:
                    self.quickMedianFilter7()

                self.cur_home_angle_filter = self.angle_dataSamples[ (self.Num - 1) / 2 ]

                if self.Num > 7:
                    print "invalid Num"
                    self.cur_home_angle_filter = x_new

        elif self.Judge_flag == 2:
            self.speed_datas[self.speed_Index] = x_new                              #在数组末增加一个新数据
            if self.speed_Index < self.Num:
                self.speed_Index += 1
                self.cur_home_speed_filter = x_new
            else:                                                             #采集到Num+1个数据后开始滤波
                self.med_filter_update()
                if self.Num == 3:
                   self.quickMedianFilter3()
                elif self.Num == 5:
                    self.quickMedianFilter5()
                elif self.Num == 7:
                    self.quickMedianFilter7()

                self.cur_home_speed_filter = self.speed_dataSamples[ (self.Num - 1) / 2 ]

                if self.Num > 7:
                    print "invalid Num"
                    self.cur_home_speed_filter = x_new

        elif self.Judge_flag == 3:
            self.acc_datas[self.acc_Index] = x_new                              #在数组末增加一个新数据
            if self.acc_Index < self.Num:
                self.acc_Index += 1
                self.cur_home_acc_filter = x_new
            else:                                                             #采集到Num+1个数据后开始滤波
                self.med_filter_update()
                if self.Num == 3:
                   self.quickMedianFilter3()
                elif self.Num == 5:
                    self.quickMedianFilter5()
                elif self.Num == 7:
                    self.quickMedianFilter7()

                self.cur_home_acc_filter = self.acc_dataSamples[ (self.Num - 1) / 2 ]

                if self.Num > 7:
                    print "invalid Num"
                    self.cur_home_acc_filter = x_new


    #数据移动
    def med_filter_update(self):
        if self.Judge_flag == 1:
            for i in range(0, self.Num):
                self.angle_dataSamples[i] = self.angle_datas[i+1]

            for i in range(0, self.Num):
                self.angle_datas[i] = self.angle_datas[i+1]

        elif self.Judge_flag == 2:
            for i in range(0, self.Num):
                self.speed_dataSamples[i] = self.speed_datas[i+1]

            for i in range(0, self.Num):
                self.speed_datas[i] = self.speed_datas[i+1]

        elif self.Judge_flag == 3:
            for i in range(0, self.Num):
                self.acc_dataSamples[i] = self.acc_datas[i+1]

            for i in range(0, self.Num):
                self.acc_datas[i] = self.acc_datas[i+1]

    #快速排序函数
    def quickMedianFilter3(self):
        self.med_sort(0,1)
        self.med_sort(1,2)
        self.med_sort(0,1)

    def quickMedianFilter5(self):
        self.med_sort(0,1)
        self.med_sort(3,4)
        self.med_sort(0,3)
        self.med_sort(1,4)
        self.med_sort(1,2)
        self.med_sort(2,3)
        self.med_sort(1,2)

    def quickMedianFilter7(self):
        self.med_sort(0,5)
        self.med_sort(0,3)
        self.med_sort(1,6)
        self.med_sort(2,4)
        self.med_sort(0,1)
        self.med_sort(3,5)
        self.med_sort(2,6)
        self.med_sort(2,3)
        self.med_sort(3,6)
        self.med_sort(4,5)
        self.med_sort(1,4)
        self.med_sort(1,3)
        self.med_sort(3,4)

    #简单排序
    def med_sort(self,i,j):
        if self.Judge_flag == 1:
            if self.angle_dataSamples[i] > self.angle_dataSamples[j]:
                data_temp = self.angle_dataSamples[j]
                self.angle_dataSamples[j] = self.angle_dataSamples[i]
                self.angle_dataSamples[i] = data_temp

        elif self.Judge_flag == 2:
            if self.speed_dataSamples[i] > self.speed_dataSamples[j]:
                data_temp = self.speed_dataSamples[j]
                self.speed_dataSamples[j] = self.speed_dataSamples[i]
                self.speed_dataSamples[i] = data_temp

        elif self.Judge_flag == 3:
            if self.acc_dataSamples[i] > self.acc_dataSamples[j]:
                data_temp = self.acc_dataSamples[j]
                self.acc_dataSamples[j] = self.acc_dataSamples[i]
                self.acc_dataSamples[i] = data_temp

def kbInit():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = old_settings
    # new_settings[3] = new_settings[3] & ~termios.ISIG
    new_settings[3] = new_settings[3] & ~termios.ICANON
    new_settings[3] = new_settings[3] & ~termios.ECHONL
    print 'old setting %s' % (repr(old_settings))
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_settings)

def kbhit():
    fd = sys.stdin.fileno()
    r = select.select([sys.stdin],[],[],0.01)
    rcode = ''
    if len(r[0]) >0:
        rcode  = sys.stdin.read(1)
    return rcode

'''
def global_init(device):
    device['var'] = {}
    device['var']['goal'] = 20
'''

def Motor_Init(device):
    device['run']={}

    #设置两个飞轮
    # motor address
    device['run']['motorg1']=motor.Motor(35)#
    device['run']['motorg2']=motor.Motor(33)#


    #设置四个轮子
    device['run']['motorv1']=motor.Motor(18)#
    device['run']['motorv2']=motor.Motor(17)#
    device['run']['motorh1']=motor.Motor(20)#
    device['run']['motorh2']=motor.Motor(19)#


    #设置两个偏摆
    device['run']['motorw1']=motor.Motor(52)#52
    device['run']['motorw2']=motor.Motor(51)#51


    # motor current speed
    device['run']['motorhs']=0
    device['run']['motorvs']=0
    # motor target speed
    device['run']['motorhp']=0
    device['run']['motorvp']=0
    print 'Motor_Init Done'

def MPU6050_Init(device):
    device['stand']={}
    device['stand']['home']=mpu6050.MPU6050('usb-3f980000.usb-1.5')     #圆盘姿态传感器
    device['stand']['homex']=0
    device['stand']['homey']=0
    # device['stand']['runout'] = mpu6050.MPU6050('usb-3f980000.usb-1.2') #飞轮偏摆姿态传感器
    device['stand']['runout2'] = mpu6050.MPU6050('usb-3f980000.usb-1.4') #飞轮偏摆姿态传感器2
    device['stand']['runoutx'] = 0
    device['stand']['runouty'] = 0
    time.sleep(1)
    print 'MPU6050_Init Done'

# direction run
def Motor_goto(device, direction, angle_stand):
    while (direction > 360):
        direction = direction - 360
    while (direction < 0):
        direction = direction + 360
    #angle_stand = 80
    direction = float(direction) / 180.0 * 3.14159265358979
    angle_stand = float(angle_stand) / 180.0 * 3.14159265358979

    device['run']['motorvp'] = int((math.asin(math.sin(angle_stand) * math.sin(direction))) * 180.0 / 3.14159265358979)
    device['run']['motorhp'] = int((math.asin(math.sin(angle_stand) * math.cos(direction))) * 180.0 / 3.14159265358979)
    print device['run']['motorvp'],"---",device['run']['motorhp']

# coordinate transformation matrix of x axis(unit:radian)
def Rotx(x):
    matrix = np.mat([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    return matrix

# coordinate transformation matrix of y axis
def Roty(y):
    matrix = np.mat([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    return matrix

# coordinate transformation matrix of z axis
def Rotz(z):
    matrix = np.mat([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return matrix

# 圆盘姿态角解算，输入传感器数据（弧度），输出圆盘前行方向的倾角
def Attitude_plant(x,y,z):
    mat_mpu = Rotz(z) * Roty(y) * Rotx(x)           #mpu相对于惯性系的坐标变换矩阵
    forward_mpu = np.mat([[-1],[1],[0]])                     #前进方向向量在mpu坐标系中的坐标
    forward_ins = mat_mpu * forward_mpu             #前进方向向量在惯性系中的坐标
    x = forward_ins[0,0]
    y = forward_ins[1,0]
    z = forward_ins[2,0]
    #print "x == ",x," y == ",y," z == ",z
    return math.atan(z / math.hypot(x,y))           #圆盘前进方向的倾角(弧度)

def Attitude_plant_roll(x,y,z):
    mat_mpu = Rotz(z) * Roty(y) * Rotx(x)           #mpu相对于惯性系的坐标变换矩阵
    forward_mpu = np.mat([[1],[1],[0]])                     #侧向方向向量在mpu坐标系中的坐标
    forward_ins = mat_mpu * forward_mpu             #前进方向向量在惯性系中的坐标
    x = forward_ins[0,0]
    y = forward_ins[1,0]
    z = forward_ins[2,0]
    #print "x == ",x," y == ",y," z == ",z
    return math.atan(z / math.hypot(x,y))           #圆盘前进方向的倾角(弧度)

def acc_NED(x,y,z,acc_x,acc_y,acc_z):
    mat_mpu = Rotz(z) * Roty(y) * Rotx(x)
    return mat_mpu * np.mat([[acc_x],[acc_y],[acc_z]])

if __name__ == '__main__':
    device = {}
    #global_init(device)
    Motor_Init(device)
    kbInit()
    MPU6050_Init(device)

    #device['remote'] = remote.Remote(20, 21)
    #device['run']['motorg1'].set_speed(-5000)
    #device['run']['motorg2'].set_speed(5000)
    #time.sleep(150)

    #angle_stand = 0									#圆盘期望角度（圆盘闭环控制）
    speed_direction = 5
    speed_direction_last = 5
    speed_run = 0
    speed_run_changeflag = 0
    speed_wheel = 0
    speed_wheel_changeflag = 0
    speed_run_or_direction_change = 0

    power17 = 0
    power18 = 0
    power19 = 0
    power20 = 0
    #goal = 30

    #device['run']['motorw1'].set_abs_position(55000)
    #device['run']['motorw2'].set_abs_position(55000)
    #Motor_goto(device, 45, 80)

    ts = TimerThread(device)
    ts.setDaemon(True)
    ts.start()					#run函数在这里开始运行

    js = jm.JoystickThread()
    js.setDaemon(True)
    js.start()

    print 'main start:'
    # device['run']['motorg1'].disable()
    # device['run']['motorg2'].disable()
    # device['run']['motorw1'].disable()
    # device['run']['motorw2'].disable()
    while True:
        c = kbhit()										#获取键盘指令
        param_flag = move_or_param % 2                  #小键盘控制指令（0：运动方向控制；1：PID参数调整）

        if len(c) != 0:
            #运动方向控制,对应小键盘上的方向
            if c == '9':
                if param_flag == 0:
                    power17 = 1
                    power18 = -1
                    power19 = 0
                    power20 = 0
                    speed_direction = 9
                else:
                    Ap -= 0.002
                    if Ap < 0:
                        Ap = 0
                    ts.accPID.setKp(Ap)
                    print "Ap == ",Ap

            elif c == '8':
                if param_flag == 0:
                    # power17 = 0.707
                    # power18 = -0.707
                    # power19 = -0.707
                    # power20 = 0.707
                    # speed_direction = 8
                    pass
                else:
                    Vp += 0.1
                    ts.speedPID.setKp(Vp)
                    print "Vp == ",Vp
            elif c == '7':
                if param_flag == 0:
                    power17 = 0
                    power18 = 0
                    power19 = -1
                    power20 = 1
                    speed_direction = 7
                else:
                    Ap += 0.002
                    ts.accPID.setKp(Ap)
                    print "Ap == ",Ap

            elif c == '4':
                if param_flag == 0:
                    # power17 = -0.707
                    # power18 = 0.707
                    # power19 = -0.707
                    # power20 = 0.707
                    # speed_direction = 4
                    pass
                else:
                    Ai += 0.001
                    ts.accPID.setKi(Ai)
                    print "Ai == ",Ai
            elif c == '1':
                if param_flag == 0:
                    power17 = -1
                    power18 = 1
                    power19 = 0
                    power20 = 0
                    speed_direction = 1
                else:
                    Vi += 0.1
                    ts.speedPID.setKi(Vi)
                    print "Vi == ",Vi
            elif c == '2':
                if param_flag == 0:
                    # power17 = -0.707
                    # power18 = 0.707
                    # power19 = 0.707
                    # power20 = -0.707
                    # speed_direction = 2
                    pass
                else:
                    Vi -= 0.1
                    if Vi < 0:
                        Vi = 0
                    ts.speedPID.setKi(Vi)
                    print "Vi == ",Vi
            elif c == '3':
                if param_flag == 0:
                    power17 = 0
                    power18 = 0
                    power19 = 1
                    power20 = -1
                    speed_direction = 3
#                 Ad -= 0.5
#                 if Ad < 0:
#                     Ad = 0
#                 ts.accPID.setKd(Ad)
#                 print "Ad == ",Ad

            elif c == '6':
                if param_flag == 0:
                    # power17 = 0.707
                    # power18 = -0.707
                    # power19 = 0.707
                    # power20 = -0.707
                    # speed_direction = 6
                    pass
                else:
                    Ai -= 0.001
                    if Ai < 0:
                        Ai = 0
                    ts.accPID.setKi(Ai)
                    print "Ai == ",Ai
            elif c == '5':
                if param_flag == 0:
                    power17 = 0
                    power18 = 0
                    power19 = 0
                    power20 = 0
                    speed_direction = 5
                else:
                    Vp -= 0.1
                    if Vp < 0:
                        Vp = 0
                    ts.speedPID.setKp(Vp)
                    print "Vp == ",Vp
            elif c == ',':
                Vd += 0.1
                ts.speedPID.setKd(Vd)
                print "Vd == ",Vd
            elif c == '.':
                Vd -= 0.1
                if Vd < 0:
                    Vd = 0
                ts.speedPID.setKd(Vd)
                print "Vd == ",Vd

            elif c == 'u':
                Sp += 0.05
                ts.positionPID.setKp(Sp)
            elif c == 'i':
                Sp -= 0.05
                if Sp < 0:
                    Sp = 0
                ts.positionPID.setKp(Sp)

            elif c == 'o':
                Si += 0.02
                ts.positionPID.setKi(Si)
            elif c == 'p':
                Si -= 0.02
                if Si < 0:
                    Si = 0
                ts.positionPID.setKi(Si)
            elif c == '[':
                Sd += 0.01
                ts.positionPID.setKd(Sd)
            elif c == ']':
                Sd -= 0.01
                if Sd < 0:
                    Sd = 0
                ts.positionPID.setKd(Sd)

            elif c == 'e':
                YP +=10
                ts.YspeedPID.setKp(YP)     #侧向角速度P值
            elif c == 'h':
                YP-= 10
                if YP<0:
                   YP = 0
                ts.YspeedPID.setKp(YP)
            elif c == 'c':
                YI +=0.1
                ts.YspeedPID.setKi(YI)    #侧向角速度I值
                print"YI",YI
            elif c == 'x':
                YI-= 0.1
                if YI < 0:
                    YI = 0
                ts.YspeedPID.setKi(YI)     #侧向角速度D值
                print"YI",YI
            elif c == 'y':
                YD += 1
                ts.YspeedPID.setKd(YD)
                print"YD",YD
            elif c == 'w':
                YD -= 1
                if YD < 0:
                    YD = 0
                ts.YspeedPID.setKd(YD)
                print"YD",YD
            elif c == '-':
                print_flag += 1                         #切换打印参数
            elif c == '+':
                move_or_param += 1                      #小键盘指令切换（控制运动，或者，调节参数）

                power17 = 0
                power18 = 0
                power19 = 0
                power20 = 0
                speed_direction = 5

            # elif c == 'r':								#麦轮加速
            #     speed_run += 1000
            #     if speed_run > 3500:
            #         speed_run = 3500
            #     speed_run_changeflag = 1
            #     print "set speed_run == ", speed_run
            # elif c == 't':								#麦轮减速
            #     speed_run -= 1000
            #     if speed_run < -3500:
            #         speed_run = -3500
            #     speed_run_changeflag = 1
            #     print "set speed_run == ", speed_run

            elif c == '5':								#麦轮电机速度设置为0
                speed_run = 0
                speed_direction = 5
                speed_run_changeflag = 1
                print "set speed_run == 0"

            #飞轮速度控制
            # elif c == 'f':								#飞轮加速
            #     speed_wheel += 1000
            #     if speed_wheel > 10000:
            #         speed_wheel = 10000
            #     speed_wheel_changeflag = 1
            #     print "set speed_wheel =", speed_wheel
            # elif c == 'g':								#飞轮减速
            #     speed_wheel -= 1000
            #     if speed_wheel < - 10000:
            #         speed_wheel = -10000
            #     speed_wheel_changeflag = 1
            #     print "set speed_wheel =", speed_wheel
            # elif c == '0':								#飞轮电机速度设置为0
            #     speed_wheel = 0
            #     speed_wheel_changeflag = 1
            #     print "set speed_wheel == 0"
            # elif c == 'a':								#获取飞轮速度
            #     print device['run']['motorg1'].get_speed()
            #     print device['run']['motorg2'].get_speed()

            elif c == 'z':
                ts.print_end += 1

            elif c == 'm':
                ts.mgoback += 1
            elif c == 'n':
                ts.mgoback_oppsite += 1

            # elif c == 'm':
            #     Gain -= 0.1
            #     print "Gain == ",Gain
            # elif c == 'n':
            #     Gain += 0.1
            #     print "Gain == ",Gain

            #翻越台阶
            # elif c == 'v':
            #     speed_run = 3500
            #     print "jump speed_run == ", speed_run

            # elif c == 'b':
            #     manual_back_flag += 1
            #     if manual_back_flag % 2 == 0 :
            #         print "manual_back OFF ... manual_back_flag == ", manual_back_flag
            #     elif manual_back_flag % 2 == 1 :
            #         print "manual_back ON ... manual_back_flag == ", manual_back_flag

            #PID参数调节
            #侧向PID调节

            # elif c == 's' or c == 'S':
            #     stop_flag += 1

            #     if stop_flag % 2 == 1:
            #         print "Stop!",stop_flag
            #         device['run']['motorv1'].set_speed(0)
            #         device['run']['motorv2'].set_speed(0)
            #         device['run']['motorh1'].set_speed(0)
            #         device['run']['motorh2'].set_speed(0)
            #         device['run']['motorv1'].disable()
            #         device['run']['motorv2'].disable()
            #         device['run']['motorh1'].disable()
            #         device['run']['motorh2'].disable()
            #     elif stop_flag % 2 == 0:
            #         print "Start again!",stop_flag
            #         device['run']['motorv1'].enable()
            #         device['run']['motorv2'].enable()
            #         device['run']['motorh1'].enable()
            #         device['run']['motorh2'].enable()

            elif c == 'k' or c == 'K':
                print "Start to Exit the program!"
                ts.stop()
                # f.close() #关闭文件
                time.sleep(0.3)

                print "set speed ==  0"
                device['run']['motorv1'].set_speed(0)
                device['run']['motorv2'].set_speed(0)
                device['run']['motorh1'].set_speed(0)
                device['run']['motorh2'].set_speed(0)
                device['run']['motorg1'].set_speed(0)
                device['run']['motorg2'].set_speed(0)
                device['run']['motorw1'].set_speed(0)
                device['run']['motorw2'].set_speed(0)
                print "disabling motors"
                device['run']['motorv1'].disable()
                device['run']['motorv2'].disable()
                device['run']['motorh1'].disable()
                device['run']['motorh2'].disable()
                device['run']['motorg1'].disable()
                device['run']['motorg2'].disable()
                device['run']['motorw1'].disable()
                device['run']['motorw2'].disable()
                print "completed, then exit()"
                exit()
                print "Killed"
#        else :
#            Motor_goto(device, 0, 0)
#            print 'K %x'%(ord(c))
        time.sleep(0.1)

        # 通过手柄设置麦轮速度 左摇杆前后
        speed_run = (-1)*js.axis_states['y']*3500
        # 通过手柄设置飞轮速度
        if js.button_states['x'] == 1:                              #飞轮加速 X键
            speed_wheel += 1000
            if speed_wheel > 10000:
                speed_wheel = 10000
            speed_wheel_changeflag = 1
            print "set speed_wheel =", speed_wheel
        if js.button_states['y'] == 1:                              #飞轮减速 Y键
            speed_wheel -= 1000
            if speed_wheel < - 10000:
                speed_wheel = -10000
            speed_wheel_changeflag = 1
            print "set speed_wheel =", speed_wheel
        if js.button_states['a'] == 1:                              #获取飞轮速度 A键
            print device['run']['motorg1'].get_speed()
            print device['run']['motorg2'].get_speed()
        # 通过手柄手动回中 B键
        if js.button_states['b'] == 1:
            manual_back_flag += 1
            if manual_back_flag % 2 == 0 :
                print "manual_back OFF ... manual_back_flag == ", manual_back_flag
            elif manual_back_flag % 2 == 1 :
                print "manual_back ON ... manual_back_flag == ", manual_back_flag
        # 通过手柄设置运动方向 十字键
        if js.axis_states['hat0y'] == -1.0:
            power17 = 0.707
            power18 = -0.707
            power19 = -0.707
            power20 = 0.707
            speed_direction = 8
        if js.axis_states['hat0y'] == 1.0:
            power17 = -0.707
            power18 = 0.707
            power19 = 0.707
            power20 = -0.707
            speed_direction = 2
        if js.axis_states['hat0x'] == -1.0:
            power17 = -0.707
            power18 = 0.707
            power19 = -0.707
            power20 = 0.707
            speed_direction = 4
        if js.axis_states['hat0x'] == 1.0:
            power17 = 0.707
            power18 = -0.707
            power19 = 0.707
            power20 = -0.707
            speed_direction = 6
        # 手柄控制麦轮的急停重启 RB键
        if js.button_states['tr'] == 1.0:
            stop_flag += 1
            if stop_flag % 2 == 1:
                print "Stop!",stop_flag
                device['run']['motorv1'].set_speed(0)
                device['run']['motorv2'].set_speed(0)
                device['run']['motorh1'].set_speed(0)
                device['run']['motorh2'].set_speed(0)
                device['run']['motorv1'].disable()
                device['run']['motorv2'].disable()
                device['run']['motorh1'].disable()
                device['run']['motorh2'].disable()
            elif stop_flag % 2 == 0:
                print "Start again!",stop_flag
                device['run']['motorv1'].enable()
                device['run']['motorv2'].enable()
                device['run']['motorh1'].enable()
                device['run']['motorh2'].enable()

        # 手柄控制退出程序 LB键
        if js.button_states['tl'] == 1.0:
            print "Start to Exit the program!"
            ts.stop()
            time.sleep(0.3)

            print "set speed ==  0"
            device['run']['motorv1'].set_speed(0)
            device['run']['motorv2'].set_speed(0)
            device['run']['motorh1'].set_speed(0)
            device['run']['motorh2'].set_speed(0)
            device['run']['motorg1'].set_speed(0)
            device['run']['motorg2'].set_speed(0)
            device['run']['motorw1'].set_speed(0)
            device['run']['motorw2'].set_speed(0)
            print "disabling motors"
            device['run']['motorv1'].disable()
            device['run']['motorv2'].disable()
            device['run']['motorh1'].disable()
            device['run']['motorh2'].disable()
            device['run']['motorg1'].disable()
            device['run']['motorg2'].disable()
            device['run']['motorw1'].disable()
            device['run']['motorw2'].disable()
            print "completed, then exit()"
            exit()
            print "Killed"

        if js.button_states['start'] == 1.0:
            ts.up_flag = 1
            ts.up_start_time = time.time()

        # 手柄控制麦轮左右行进(试图通过手柄人工调节直线行走)  右摇杆左右
        speed_lateral = js.axis_states['rx']*500

        #设置麦轮速度
        if speed_direction != speed_direction_last or speed_run_changeflag == 1:
            speed_direction_last = speed_direction
            speed_run_changeflag = 0
            speed_run_or_direction_change = 1											#运动方向改变标志
            print "speed_run change, direction:",speed_direction

        # #设置麦轮速度
        # if speed_run_or_direction_change == 1:

        #     if speed_run < -3500:
        #         speed_run = -3500

        #     device['run']['motorv1'].set_speed(int(speed_run * power18))	#number18
        #     device['run']['motorv2'].set_speed(int(speed_run * power17))	#number17
        #     time.sleep(0.1)
        #     device['run']['motorh1'].set_speed(int(speed_run * power20) )	#number20
        #     device['run']['motorh2'].set_speed(int(speed_run * power19))	#number19
        #     time.sleep(0.1)
        #     speed_run_or_direction_change = 0
        #     print "set speed_run over"

        # device['run']['motorv1'].set_speed(int(ts.speed_run_18)) #number18
        # device['run']['motorv2'].set_speed(int(ts.speed_run_17)) #number17
        # device['run']['motorh1'].set_speed(int(ts.speed_run_20)) #number20
        # device['run']['motorh2'].set_speed(int(ts.speed_run_19)) #number19

        device['run']['motorv1'].set_speed(int(ts.speed_run_18 - speed_lateral)) #number18
        device['run']['motorv2'].set_speed(int(ts.speed_run_17 + speed_lateral)) #number17
        device['run']['motorh1'].set_speed(int(ts.speed_run_20 - speed_lateral)) #number20
        device['run']['motorh2'].set_speed(int(ts.speed_run_19 + speed_lateral)) #number19

        #设置飞轮速度
        if speed_wheel_changeflag == 1:
            device['run']['motorg1'].set_speed(speed_wheel)
            time.sleep(0.1)
            device['run']['motorg2'].set_speed(-speed_wheel)
            time.sleep(0.1)
            speed_wheel_changeflag = 0
            print "set speed_wheel over"

    print 'exit'
