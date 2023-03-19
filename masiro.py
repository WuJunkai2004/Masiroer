def analyze(data, method):
	result = {}
	for index in method['order']:
		if(method[index]['return']=='return'):
			return result[ method[index]['refer'] ]
		if(method[index]['type']=="regex"):
			result[index] = re.search(method[index]["rule"], data).group()
		elif(method[index]['type']=='find'):
			result[index] = re.findall(method[index]["rule"], data)
		elif(method[index]["type"]=='func'):
			pass
		elif(method[index]['type']=='range'):
			result[index] = []
			for sub in result[ method[index]['refer'] ]:
				result[index].append( analyze(sub, method[index]['method']) )
		else:
			raise RuntimeError('unknown type: {}'.format(index))
	return result
