#!/usr/bin/python
# coding: utf-8

from periphery import Serial
import base_serial
import time
import threading

BAUD_RATE = 115200
# BAUD_RATE = 921600
START_FLAG = 0x55
ACC_16G = 16 * 9.8
GYR_2000 = 2000
ANGLE_180 = 180


class MPU6050:
	class __MPU6050ReadThread(threading.Thread):
		def __init__(self, mpu6050):
			self.__mpu6050 = None
			self.__run_flag = True
			threading.Thread.__init__(self)
			self.__mpu6050 = mpu6050

		def stop(self):
			self.__run_flag = False

		def run(self):
			while self.__run_flag:
				tmp = bytearray(self.__mpu6050.device.read(11, 0.1))
				self.__mpu6050.data.extend(tmp)

	class __MPU6050DealThread(threading.Thread):
		def __init__(self, mpu6050):
			self.__mpu6050 = None
			self.__run_flag = True
			threading.Thread.__init__(self)
			self.__mpu6050 = mpu6050

		def stop(self):
			self.__run_flag = False

		def run(self):
			tmp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			while self.__run_flag:
				time.sleep(0.01)
				#print "time1111 == %f"%time.time()
				while len(self.__mpu6050.data) >= 11:
					#print "time222 == %f"%time.time()
					if self.__mpu6050.data.pop(0) == START_FLAG:
						tmp[0] = START_FLAG
						tmp[1] = self.__mpu6050.data.pop(0)
						if tmp[1] in [0x51, 0x52, 0x53]:
							tmp[2] = self.__mpu6050.data.pop(0)
							tmp[3] = self.__mpu6050.data.pop(0)
							tmp[4] = self.__mpu6050.data.pop(0)
							tmp[5] = self.__mpu6050.data.pop(0)
							tmp[6] = self.__mpu6050.data.pop(0)
							tmp[7] = self.__mpu6050.data.pop(0)
							tmp[8] = self.__mpu6050.data.pop(0)
							tmp[9] = self.__mpu6050.data.pop(0)
							tmp[10] = self.__mpu6050.data.pop(0)

							if sum(tmp[:-1]) & 0xff == tmp[10]:
								if tmp[1] == 0x51:
									x = tmp[2] | (tmp[3] << 8)
									if x & (1 << 16 - 1):
										x -= 1 << 16
									self.__mpu6050.acc_x = float(x) / 32768 * ACC_16G
									y = tmp[4] | (tmp[5] << 8)
									if y & (1 << 16 - 1):
										y -= 1 << 16
									self.__mpu6050.acc_y = float(y) / 32768 * ACC_16G
									z = tmp[6] | (tmp[7] << 8)
									if z & (1 << 16 - 1):
										z -= 1 << 16
									self.__mpu6050.acc_z = float(z) / 32768 * ACC_16G
								elif tmp[1] == 0x52:
									x = tmp[2] | (tmp[3] << 8)
									if x & (1 << 16 - 1):
										x -= 1 << 16
									self.__mpu6050.gyr_x = float(x) / 32768 * GYR_2000
									y = tmp[4] | (tmp[5] << 8)
									if y & (1 << 16 - 1):
										y -= 1 << 16
									self.__mpu6050.gyr_y = float(y) / 32768 * GYR_2000
									z = tmp[6] | (tmp[7] << 8)
									if z & (1 << 16 - 1):
										z -= 1 << 16
									self.__mpu6050.gyr_z = float(z) / 32768 * GYR_2000
								elif tmp[1] == 0x53:
									x = tmp[2] | (tmp[3] << 8)
									if x & (1 << 16 - 1):
										x -= 1 << 16
									self.__mpu6050.angle_x = float(x) / 32768 * ANGLE_180
									y = tmp[4] | (tmp[5] << 8)
									if y & (1 << 16 - 1):
										y -= 1 << 16
									self.__mpu6050.angle_y = float(y) / 32768 * ANGLE_180
									z = tmp[6] | (tmp[7] << 8)
									if z & (1 << 16 - 1):
										z -= 1 << 16
									self.__mpu6050.angle_z = float(z) / 32768 * ANGLE_180

	def __init__(self, path):
		self.device = None
		self.__t_read = None
		self.__t_deal = None
		self.data = []
		self.acc_x = 0.0
		self.acc_y = 0.0
		self.acc_z = 0.0
		self.gyr_x = 0.0
		self.gyr_y = 0.0
		self.gyr_z = 0.0
		self.angle_x = 0.0
		self.angle_y = 0.0
		self.angle_z = 0.0
		sequence = base_serial.get_usb_serial_sequence_by_path(path)
		if sequence != None:
			tty_name = "/dev/ttyUSB" + str(sequence)
			self.device = Serial(tty_name, BAUD_RATE)
			self.start()
		else:
			self.device = None

	def start(self):
		if self.__t_read == None:
			self.__t_read = MPU6050.__MPU6050ReadThread(self)
			self.__t_read.setDaemon(True)
			self.__t_read.start()
		if self.__t_deal == None:
			self.__t_deal = MPU6050.__MPU6050DealThread(self)
			self.__t_deal.setDaemon(True)
			self.__t_deal.start()

	def stop(self):
		if self.__t_read != None:
			self.__t_read.stop()
		if self.__t_deal != None:
			self.__t_deal.stop()


if __name__ == '__main__':
	mpu6050_pan = MPU6050('usb-3f980000.usb-1.4')
	mpu6050_head = MPU6050('usb-3f980000.usb-1.5')
	mpu6050_runout = MPU6050('usb-3f980000.usb-1.2')
	while True:
		print "%s %.6f %.3f %.3f %.3f" % ("pan",  time.time(), mpu6050_pan.angle_x, mpu6050_pan.angle_y, mpu6050_pan.angle_z)
		# print "%s %.6f %.3f %.3f %.3f" % ("head",  time.time(), mpu6050_head.angle_x, mpu6050_head.angle_y, mpu6050_head.angle_z)
		# print "%s %.6f %.9f %.9f %.9f" % ("runout", time.time(), mpu6050_runout.angle_x, mpu6050_runout.angle_y, mpu6050_runout.angle_z)
		# print "%s %.6f %.3f %.3f %.6f" % ("runout",  time.time(), mpu6050_pan.angle_x,  mpu6050_pan.angle_y,  mpu6050_pan.angle_z)
		#print "%s %.6f %.6f %.6f %.6f" % ("pan",  time.time(), mpu6050_head.gyr_x, mpu6050_head.gyr_y, mpu6050_head.gyr_z)
		time.sleep(0.01)

