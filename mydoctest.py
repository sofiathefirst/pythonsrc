"""
>>> add(3,4)
7
>>> cnt('xxxddddd')
'x3d5'
>>> cnt('x')
'x1'
"""
def cnt(strd):
	out =''
	cntt = 1
	s = strd[0]
	for i in range(len(strd)-1):
		if strd[i+1]==s:
			cntt+=1
		else:
			out = out+s+str(cntt)
			cntt = 1
			s=strd[i+1]
	out = out+s+str(cntt)
	return out
		
	
def add(x,y):
	return x+y
if __name__ == "__main__":
    import doctest
    doctest.testmod()
