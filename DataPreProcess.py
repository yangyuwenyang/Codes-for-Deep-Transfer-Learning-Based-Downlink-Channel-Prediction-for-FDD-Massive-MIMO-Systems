import numpy as np
import re

'''Globel parameters'''
Max_path = 30  # max number of paths
Max_users=3000
Number_antenna = 64
B = 2e4

'''Channel generation'''


def channel_generator(path_list):
	channel = np.zeros([Number_antenna, 1], dtype=np.complex)
	a_x = lambda phi_az, phi_ele, M: [np.exp(1j * np.pi * np.sin(phi_ele) * np.cos(phi_az) * i) for i in range(M)]
	for channel_path in path_list:
		path_loss_dB, path_phase, path_delay, AOA_ele_D, AOA_az_D = channel_path
		AOA_ele = AOA_ele_D / 180 * np.pi
		AOA_az = AOA_az_D / 180 * np.pi
		path_phase = path_phase / 180 * np.pi
		a_A_x = np.array(a_x(AOA_az, AOA_ele, Number_antenna), dtype=np.complex).reshape([Number_antenna, 1])
		path_loss = 10 ** (path_loss_dB / 10)
		channel += np.sqrt(path_loss) * np.exp(1j * (path_phase + 2 * np.pi * path_delay * B)) * a_A_x
	return channel.reshape((Number_antenna,))

'''Rename the output file'''
import shutil
def rename_output_file():
	for id_area in ID_inf:
		for bs_fre in enumerate(BS_frequency):
			filename = 'I://Model_Define//TRY1//TRY3//study//try3.paths.t001_' + str(bs_fre[0] + 1).zfill(
				2) + '.r0' + id_area + '.p2m'
			newfilename = 'I://Model_Define//DataPrepro//BS' + str(bs_fre[1]) + 'area' + id_area + '.p2m'
			shutil.copy(filename, newfilename)
			print(filename)

'''Exactraction of path parameter from .p2m file'''
import scipy.io as scio
def Exactraction_path_parameters():
	for id_area in ID_inf:
		channel_matrix_per_area = []
		for fre in BS_frequency:
			filename = 'I://Model_Define//DataPrepro//BS' + str(fre) + 'area' + id_area + '.p2m'
			channel_infor_envir = open(filename, 'r')
			channel_infor_content = channel_infor_envir.readlines()
			num_users_index = 0
			channel_sample_list = []
			found_num_user_flag = 1
			found_new_user_flag = 1
			for line in enumerate(channel_infor_content):
				if line[1][0] != '#':
					if found_num_user_flag:
						found_num_user_flag = 0
						number_user_str = line[1][0:4]
						Number_users_given_total = int(number_user_str)
						print('Found the total number of users  for frequency ', fre, ' area', id_area, ' : ',
							  Number_users_given_total,'num_ant',Number_antenna)

					if line[1][0:2] == 'Tx':
						if found_new_user_flag == 1:
							found_new_user_flag = 0
							num_users_index += 1
							print('find a new user: ', num_users_index)
							path_list_per_user = []
							path_number_extract = channel_infor_content[line[0] - 3]
							if path_number_extract.find('.') == -1:
								path_number_str = re.findall('[-Ee0-9.]+', path_number_extract)
								userindex, pathnumber = [int(i) for i in path_number_str[0:2]]
								print('the', num_users_index, '-th  user has ', pathnumber,
									  'paths and its orginial index is', userindex)
								pathnumber_index = 1
								path_infor = channel_infor_content[line[0] - 1]
								data_path_str = re.findall('[-Ee0-9.]+', path_infor)
								data_path = [float(i) for i in data_path_str[2:7]]
								path_list_per_user.append(data_path)
							else:
								num_users_index -= 1
								print('one user has no path and num_users_index-=1: ', num_users_index)

						else:
							path_infor = channel_infor_content[line[0] - 1]
							data_path_str = re.findall('[-Ee0-9.]+', path_infor)
							data_path = [float(i) for i in data_path_str[2:7]]
							path_list_per_user.append(data_path)
							if len(path_list_per_user) == Max_path or len(path_list_per_user) == pathnumber:
								found_new_user_flag = 1
								csi = channel_generator(path_list_per_user)
								channel_sample_list.append(csi)
								print('user number +1, channel finished')
					print(np.asarray(channel_sample_list).shape)
					if len(channel_sample_list) == Number_users_given_total:
						print('all users has paths and then break')
						print('the number of users in datasets is: ', len(channel_sample_list))
						break
					elif len(channel_sample_list) == Max_users:
						print('the number of users is enough: ', Max_users, 'and then break')
						print('the number of users in datasets is: ', len(channel_sample_list))
						break
			if len(channel_sample_list) % area_unit:
				temp_len = len(channel_sample_list)
				channel_sample_list = channel_sample_list[0:temp_len - temp_len % area_unit]
				print('The orginal users in area ', id_area, ' is ', temp_len, ' but round to ',
					  len(channel_sample_list))
			channel_matrix_per_area.append(channel_sample_list)
			print('channel_sample_list', np.asarray(channel_sample_list).shape)
			print('channel_matrix_per_area', np.asarray(channel_matrix_per_area).shape)
			dataNew = './DataSave/channel_matrix_area' + str(id_area)+str(Number_antenna)+'.mat'
			scio.savemat(dataNew, {'channel_matrix_area': channel_matrix_per_area})
			channel_infor_envir.close()


# BS_frequency=np.arange(1000,2982,60)
BS_frequency=np.arange(1000,2982,60)
ID_area=np.arange(37,200,1)
ID_inf=[str(ind) for ind in ID_area]
area_unit=25

# rename_output_file()
# Exactraction_path_parameters()
# +str(Number_antenna)

diff=2
Source_Task_list=[]
Target_Task_list=[]
for id_area in ID_inf:
	dataNew = './DataSave/channel_matrix_area'+str(id_area) +str(Number_antenna)+'.mat'
	data_matrix = scio.loadmat(dataNew)
	channel_matrix_area = data_matrix['channel_matrix_area']
	temp_num_user = np.shape(channel_matrix_area)[1]
	times=temp_num_user//(area_unit)
	for task_index in range(times):
		channel_matrix_task=channel_matrix_area[:,task_index:task_index+area_unit,:]
		# print('testing code: shape of source channel_matrix_task is ', np.shape(channel_matrix_task))
		if (task_index+3)%9 !=0: #Source_Task
			channel_pairs_task = []
			for fre_index in range(len(channel_matrix_task)  - diff):
				channel_uplink = channel_matrix_task[fre_index]
				channel_downlink = channel_matrix_task[fre_index + diff]
				for user_index in range(len(channel_uplink)):
					uplink_channel_real = np.concatenate(
						(np.real(channel_uplink[user_index]), np.imag(channel_uplink[user_index])))
					downlink_channel_real = np.concatenate(
						(np.real(channel_downlink[user_index]), np.imag(channel_downlink[user_index])))
					pair = np.array([uplink_channel_real, downlink_channel_real])
					# print('testing code: shape of source pair is ', np.asarray(pair).shape)
					channel_pairs_task.append(pair)
			# print('testing code: shape of source channel_pairs_task is ', np.asarray(channel_pairs_task).shape)
			Source_Task_list.append(channel_pairs_task)
		elif (task_index+3)%3 !=0:# target task
			channel_pairs_task = []
			for fre_index in range(len(channel_matrix_task) - diff):
				channel_uplink = channel_matrix_task[fre_index]
				channel_downlink = channel_matrix_task[fre_index + diff]
				for user_index in range(len(channel_uplink)):
					uplink_channel_real = np.concatenate(
						(np.real(channel_uplink[user_index]), np.imag(channel_uplink[user_index])))
					downlink_channel_real = np.concatenate(
						(np.real(channel_downlink[user_index]), np.imag(channel_downlink[user_index])))
					pair = np.array([uplink_channel_real, downlink_channel_real])
					channel_pairs_task.append(pair)
			# print('testing code: shape of target channel_pairs_task is ', np.asarray(channel_pairs_task).shape)
			Target_Task_list.append(channel_pairs_task)
print('testing code: shape of Source_Task_list is ', np.asarray(Source_Task_list).shape)
print('testing code: shape of Target_Task_list is ', np.asarray(Target_Task_list).shape)
x1,x2,_,_=np.asarray(Source_Task_list).shape
y1,y2,_,_=np.asarray(Target_Task_list).shape

dataNew = './DataSave/samples_source' +str(Number_antenna)+'_'+str(x1)+'_'+str(diff)+'.mat'
scio.savemat(dataNew, {'Source_Task_list': np.asarray(Source_Task_list)})
print('stored in ',dataNew)
dataNew = './DataSave/samples_target'+str(Number_antenna)+'_'+str(y1)+'_'+str(diff)+'.mat'
scio.savemat(dataNew, {'Target_Task_list': np.asarray(Target_Task_list)})
print('stored in ',dataNew)
