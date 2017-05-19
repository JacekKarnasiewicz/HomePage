import io

import matplotlib
matplotlib.use('Agg')
matplotlib.rc('font', family='Comic Sans MS')
import matplotlib.pyplot as plt
from PIL import Image

from django.http import HttpResponse


class GenerateJuliaSet:
	"""
		Class creates PIL image and appropriate django response

		:param real_part: Real part for complex number of c from f(z) = z**2 + c (complex quadratic polynomial)
		:type real_part: 'float'
		:param imaginary_part: Imaginary part for complex number of c from f(z) = z**2 + c (complex quadratic polynomial)
		:type imaginary_part: 'float'
		:param width: Width of the picture
		:type width: 'int', default value set to 1000
		:param max_interations: Maximum amount of iterations per pixel
		:type max_interations: 'int', default value set to 255
		:param sample: Name for one of predefined samples
		:type sample: 'str'

		Each pxel is calculated in loop, which can be run unspecified amount of times

		Coordinates with fewer iterations have darker color, on the other hand coordinates
		with many iterations have lighter color
	"""
	examples = {'fern': (-0.62772, -0.42193), 'snowflake': (0.0523, 0.65), 'snail': (0.285, 0.01), 'cracks': (0, -0.8),
				'stars': (0.23686060081761018, -0.6047908282494889)}

	def __init__(self, real_part=0, imaginary_part=0, width=1000, max_iterations=255,  sample=None):
		""" Area of ​​complex space for analysis """
		self.x1, self.x2, self.y1, self.y2 = -1.8, 1.8, -1.8, 1.8
		self.real_part = real_part
		self.imaginary_part = imaginary_part
		self.width = width
		self.max_iterations = max_iterations
		if sample:
			coordinates = GenerateJuliaSet.examples.get(sample, None)
			if coordinates:
				self.real_part, self.imaginary_part = coordinates

		self.values_list = self.calculate_coordinates(width, max_iterations)

	def calculate_coordinates(self, width, max_iterations):
		"""
			Create a coordinate list(zs) and parameters(cs) from complex numbers,
			Building Julia's collection
		"""
		x_step = (float(self.x2 - self.x1) / float(width))
		y_step = (float(self.y1 - self.y2) / float(width))
		x = []
		y = []
		ycoord = self.y2
		while ycoord > self.y1:
			y.append(ycoord)
			ycoord += y_step
		xcoord = self.x1
		while xcoord < self.x2:
			x.append(xcoord)
			xcoord += x_step
			# Create a coordinate list and start condition for each cell
			# Note that the initial condition is a constant that can easily be removed
			# A constant is used to simulate an actual scenario with several inputs
			# passed to an example function
		zs = []
		cs = []
		for ycoord in y:
			for xcoord in x:
				zs.append(complex(xcoord, ycoord))
				cs.append(complex(self.real_part, self.imaginary_part))

		output = self.calculate_z_serial(max_iterations, zs, cs)
		return output 

	def calculate_z_serial(self, maxiter, zs, cs):
		""" Calculating list output using the Julia collection update rule """
		output = [0] * len(zs)
		for i in range(len(zs)):
			n = 0
			z = zs[i]
			c = cs[i]
			while abs(z) < 2 and n < maxiter:
				z = z * z + c
				n += 1
			output[i] = n
		return output

	def create_response(self):
		""" Creating PIL image and HttpResponse """
		img = Image.new('RGB', (self.width, self.width), 'black')
		pixel_map = img.load()

		for i in range(img.size[0]):
			for j in range(img.size[1]):
				value = self.values_list[self.width*i+j]
				color = int((255/self.max_iterations)*value)
				pixel_map[i, j] = (color, color, color)

		f = io.BytesIO()
		img.save(f, format='BMP')

		response = HttpResponse(f.getvalue(), content_type='image/bmp')
		response['Content-Disposition'] = 'attachment; filename=fractal(real_{})(imag_{}).bmp'.format(self.real_part, self.imaginary_part)
		return response


class PlotGraph:
	""" 
		Class creates matplotlib graph and appropriate django response

		:param data_frama: Data for graph
		:type data_frame: Pandas DataFrame object
		:param title: Graph title
		:type title: 'str', default value set to 'graph'
		:param x_label: Label name for x's
		:type x_label: 'str', default value set to 'X'
		:param y_label: Label name for y's
		:type y_label: 'str', default value set to 'Y'
		:param extension: Extension for created file
		:type extension: 'str', default value set to 'svg'
		:param style: Matplotlib pyplot style, matplotlib.style.available for more examples
		:type style: 'str', default value set to 'seaborn-dark-palette'
    """

	def __init__(self, data_frame, title='graph', x_label='X', y_label='Y', extension='svg', style='seaborn-dark-palette'):
		self.data_frame = data_frame
		self.title = title
		self.x_label = x_label
		self.y_label = y_label
		self.extension = extension
		self.style = style
		self.content_type = {'pdf': 'application/pdf', 'svg': 'image/svg+xml', 'png': 'image/png'}.get(self.extension)
		self.create_graph()

	def create_graph(self):
		""" Function creates matplotlib graph from self.data_frame """

		with plt.style.context((self.style)):
			for i in range(1, len(self.data_frame.columns)):
				plt.plot(self.data_frame[self.data_frame.columns[0]], self.data_frame[self.data_frame.columns[i]], label=self.data_frame.columns[i])

		plt.xlabel(self.x_label)
		plt.ylabel(self.y_label)
		plt.title(self.title.capitalize())
		plt.grid(True)
		plt.legend()
		plt.tight_layout()
		
	def create_response(self):
		""" Function creates django response with matplotlib graph """

		f = io.BytesIO()
		plt.savefig(f, format=self.extension)
		plt.clf()
		plt.close()
		response = HttpResponse(f.getvalue(), content_type=self.content_type)
		response['Content-Disposition'] = 'attachment; filename=graph.{0}'.format(self.extension)
		return response
