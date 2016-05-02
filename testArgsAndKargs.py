def fcn(first, *args, **kargs):
	print ("{}\n".format(type(args)))
	print ("{}\n".format(type(kargs)))

if __name__ == '__main__':
	fcn(1, 2, 3)
	fcn(first=1, second=2, third=3)
	
