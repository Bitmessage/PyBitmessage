input_val = [[12, 15], [38, 42], [45.50, 47.75]]
# output - Monday 12:00-15:00, Tuesday 14:00-18:00, Tuesday 21:30-23:45 

output = ''

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

temp_opt = []
def convert_float(obj):
	if isinstance(obj, float):
		flot = str(obj).split('.')
		return str(int(flot[0])%24)+':'+str(60*int(flot[1])/100)
	else:
		return str(obj%24)+':00'


for objs in input_val:
	if isinstance(objs[0], float) and isinstance(objs[1], float):
		# import pdb;pdb.set_trace()
		# flot = str(obj).split('.')
		# opt.append(str(int(flot[0])%24)+':'+str(60*int(flot[1])/100))
		temp_opt = '{}-{}'.format(convert_float(objs[0]),convert_float(objs[1]))
		# print(convert_float(objs[0]),convert_float(objs[1]))
	elif isinstance(objs[0], int) or isinstance(objs[1], float):
		temp_opt = '{}-{}'.format(convert_float(objs[0]),convert_float(objs[1]))
		# print(convert_float(objs[0]),convert_float(objs[1]))
	elif isinstance(objs[0], float) or isinstance(objs[1], int):
		temp_opt = '{}-{}'.format(convert_float(objs[0]),convert_float(objs[1]))
		# print(convert_float(objs[0]),convert_float(objs[1]))
	else:
		temp_opt = '{}-{}'.format(convert_float(objs[0]),convert_float(objs[1]))
		# print(convert_float(objs[0]),convert_float(objs[1]))
print(temp_opt)



	# opt = []
	# for obj in objs:
	# 	day_obj = 0
	# 	if isinstance(obj, float):
	# 		flot = str(obj).split('.')
	# 		# import pdb;pdb.set_trace()
	# 		opt.append(str(int(flot[0])%24)+':'+str(60*int(flot[1])/100))
	# 	else:
	# 		opt.append(str(obj%24)+':00')
	# 	day_obj = obj%24/24.0
	# day_obj = days[int(objs[0]/24)] if isinstance(objs[0], float) else days[int(objs[0]/24)]
	# # print(day_obj)
	# print '-'.join(opt)
