#!/usr/bin/env python

import select
import mti_device
import math
import pdb
import time
import numpy
from math import pi, radians

import threading
global imu_mutex
imu_mutex = threading.Lock()
class XSensDriver(threading.Thread):

	ENU = numpy.identity(3)
	# NED = numpy.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
	# NWU = numpy.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])

	def __init__(self):
		threading.Thread.__init__(self)
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
		self.Roll = 0.0
		self.Pitch = 0.0
		self.Yaw = 0.0
		self.w = 0.0
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.__run_flag = True


		# device = get_param('~device', 'auto')
		# device = "/dev/ttyUSB2"
		device = "auto"
		# baudrate = get_param('~baudrate', 0)
		# baudrate = 115200
		baudrate = 0
		if device == 'auto':
			devs = mti_device.find_devices()
			if devs:
				device, baudrate = devs[0]
				print("Detected MT device on port %s @ %d bps" % (device,
						baudrate))
			else:
				print("Fatal: could not find proper MT device.")
				print("Could not find proper MT device.")
				return
		if not baudrate:
			baudrate = mti_device.find_baudrate(device)
		if not baudrate:
			print("Fatal: could not find proper baudrate.")
			print("Could not find proper baudrate.")
			return

		if not baudrate:
			baudrate = mti_device.find_baudrate(device)
		if not baudrate:
			print("Fatal: could not find proper baudrate.")
			print("Could not find proper baudrate.")
			return

		print("MT node interface: %s at %d bd." % (device, baudrate))
		self.mt = mti_device.MTDevice(device,baudrate)

		# frame_local = get_param('~frame_local', 'ENU')
		# frame_local_imu = get_param('~frame_local_imu', 'ENU')
		frame_local = "ENU"
		frame_local_imu = "ENU"

		if frame_local == 'ENU':
			R = XSensDriver.ENU
		elif frame_local == 'NED':
			R = XSensDriver.NED
		elif frame_local == 'NWU':
			R = XSensDriver.NWU

		if frame_local_imu == 'ENU':
			R_IMU = XSensDriver.ENU
		elif frame_local_imu == 'NED':
			R_IMU = XSensDriver.NED
		elif frame_local_imu == 'NWU':
			R_IMU = XSensDriver.NWU

		self.R = R.dot(R_IMU.transpose())

	def stop(self):
		self.__run_flag = False

	def  run(self):
		while self.__run_flag:
			# time.sleep(0.01)
			def  broPressureToHeight(value):
				c1 = 44330.0
				c2 = 9.869232667160128300024673081668e-6
				c3 = 0.1901975534856
				intermediate = 1-math.pow(c2*value, c3)
				height = c1*intermediate
				return height

			data = self.mt.read_measurement()
			orient_data = data.get('Orientation Data')
			velocity_data = data.get('Velocity')
			position_data = data.get('Latlon')
			altitude_data = data.get('Altitude')
			acc_data = data.get('Acceleration')
			gyr_data = data.get('Angular Velocity')
			mag_data = data.get('Magnetic')
			pressure_data = data.get('Pressure')
			time_data = data.get('Timestamp')
			gnss_data = data.get('Gnss PVT')
			status = data.get('Status')

			pub_imu = False
			pub_mag = False
			pub_ori = False
			pub_twistupdate = False
			pub_pressure_height = False
			pub_fix_velocity = False
			pub_fix = False
			global imu_mutex
			imu_mutex.acquire()

			if acc_data:
				if 'Delta v.x' in acc_data: # found delta-v's
					pub_imu = False
					
				elif 'accX' in acc_data: # found acceleration
	  				pub_imu = True
					self.acc_x = acc_data['accX']
					self.acc_y = acc_data['accY']
					self.acc_z = acc_data['accZ']
					# print self.acc_x,self.acc_y,self.acc_z,'klsdkldkldfkl'
					pub_twistupdate = False

				else:
					raise MTException("Unsupported message in XDI_AccelerationGroup.")

			if gyr_data:
				if 'Delta q0' in gyr_data: # found delta-q's
					pub_imu = False
					
				elif 'gyrX' in gyr_data: # found rate of turn
	  				pub_imu = True
					self.gyr_x = gyr_data['gyrX']
					self.gyr_y = gyr_data['gyrY']
					self.gyr_z = gyr_data['gyrZ']

					pub_twistupdate = False
					
				else:
					raise MTException("Unsupported message in XDI_AngularVelocityGroup.")

				if mag_data:
					# magfield
					pub_mag = False

				if pressure_data:
					pub_pressure_height = False

				if gnss_data:
					pub_fix = False
					pub_fix_velocity = False

				if orient_data:
					if 'Q0' in orient_data:
						pub_imu = True
						# orientation
						# imu_msg.orientation.w = orient_data['Q0']
						# imu_msg.orientation.x = orient_data['Q1']
						# imu_msg.orientation.y = orient_data['Q2']
						# imu_msg.orientation.z = orient_data['Q3']

						self.w = orient_data['Q0']
						self.x = orient_data['Q1']
						self.y = orient_data['Q2']
						self.z = orient_data['Q3']

						# self.angle_x = math.atan2(2*(w*x + y*z),1-2*(x*x + y*y))
						# self.angle_y = math.asin(2*(w*y -z*x))
						# self.angle_z = math.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
						# # print angle_x

	 				elif 'Roll' in orient_data:
						pub_ori = False
						self.Roll = orient_data['Roll']
						self.Pitch = orient_data['Pitch']
						self.Yaw = orient_data['Yaw']

					else:
						raise MTException('Unsupported message in XDI_OrientationGroup')
			imu_mutex.release()
				# publish available information
				# if pub_imu:

				# if pub_mag:

				# if pub_pressure_height:

				# if pub_ori:

				# if pub_fix:

				# if pub_fix_velocity:

				# if pub_twistupdate:

def main():
	
	driver = XSensDriver()
	driver.start()
	#while True:
	#	driver.spin_once()
	#	time.sleep(0.1)
	#	
	# while True:
	# 	print driver.acc_z, driver.Pitch

if __name__== '__main__':
	main()
