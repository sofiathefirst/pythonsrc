start=5
end=30

startm=0.2
endm=1
a=range(start,end+1,1)
for e in a:
	print -((e-start)*1.0/(end-start)*(endm-startm)+startm) 
