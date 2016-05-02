class Test2(object):

	#__slots__ = ('x', 'y')	
	__lala
	x
	y
	z
	

	"""docstring for Test2"""
	def __init__(self, lala, x, y, z):
		super(Test2, self).__init__()
		self._lala = lala
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return "lala=%s - x=%s - y=%s, z=%s" %(self._lala, self.x, self.y, self.z)


if __name__ == '__main__':
	#main()
	t = Test2('lala', 'x', 'y', 'z')
	print(t)
