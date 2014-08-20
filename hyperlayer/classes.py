class Detector:
	"""
	A haar cascade classifier with associated settings
	
	path -- local file path of detector
	region -- x,y,w,h for running the classifier within a specific region
	minimum_size_square -- minimum size of detection bounds square
	maximum_size_square -- maximum size of detection bounds square
	scale_factor -- multiplier to scale by when interpolating cascade size between min and max
	minimum_neighbors -- how many nearby results should be found to count as a detection
	cascade -- OpenCV Haar Cascade
	"""
	
	def __init__(self, path=None, region={'x':0, 'y':0, 'w':0, 'h':0}, minimum_size_square=40, maximum_size_square=200, scale_factor=1.3, minimum_neighbors=3, cascade=None):
		self.path = path
		self.region = region
		self.minimum_size_square = minimum_size_square
		self.maximum_size_square = maximum_size_square
		self.scale_factor = scale_factor
		self.minimum_neighbors = minimum_neighbors
		self.cascade = cascade
