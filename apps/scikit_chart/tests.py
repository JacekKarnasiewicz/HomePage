import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from .views import scikit_chart


class ViewTest(TestCase):
	
	def test_scikit_chart_page_uses_correct_view(self):
		response = self.client.get(reverse('scikit_chart:scikit_chart'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, scikit_chart)

	def test_scikit_chart_page_render_correct_template(self):
		response = self.client.get(reverse('scikit_chart:scikit_chart'))

		self.assertTemplateUsed(response, 'scikit_chart/home.html')

	def test_scikit_chart_view_correct_context(self):
		response = self.client.get(reverse('scikit_chart:scikit_chart'))

		self.assertIn('group_1', response.context)
		self.assertIn('group_2', response.context)
		self.assertIn('group_3', response.context)

	def test_regresion_line_view_invalid_request_method(self):
		response = self.client.get(reverse('scikit_chart:regression_line'))

		self.assertEqual(response.status_code, 404)

	def test_regresion_line_view_valid_POST_request(self):
		data = json.dumps({
			'observations_x': [-86.86635944700461, -68.4331797235023,
							   -52.764976958525345, -41.013824884792626,
							   -32.718894009216584, -23.27188940092165,
							   -12.21198156682027, -5.299539170506904,
							   10.599078341013822, 24.193548387096783],
			'observations_y': [-77.02127659574468, -67.65957446808511,
							   -56.17021276595745, -49.787234042553195,
							   -42.97872340425532, -38.297872340425535,
							   -29.361702127659584, -26.382978723404264,
							   -18.297872340425542, -9.361702127659584]})

		response = self.client.post(
			reverse('scikit_chart:regression_line'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertIn('regression_line', response.content.decode('utf-8'))
		self.assertIn('accuracy', response.content.decode('utf-8'))
		self.assertEqual('application/json', response['Content-Type'])

	def test_regresion_line_view_inconsistent_data_in_POST_request(self):
		data = json.dumps({
			'observations_x': [-86.86635944700461, -45.58837174844149],
			'observations_y': [-77.02127659574468]})

		with self.assertRaisesRegexp(ValueError, 'inconsistent numbers of samples'):
			response = self.client.post(
				reverse('scikit_chart:regression_line'),
				HTTP_X_REQUESTED_WITH='XMLHttpRequest',
				content_type='application/json',
				data=data)

	# Add when scikit-learn version 0.19 will be available (error when passing 1d arrays as data)
	# def test_regresion_line_view_invalid_data_in_POST_request(self):
	# 	data = json.dumps({
	# 		'observations_x': [-86.86635944700461],
	# 		'observations_y': [-77.02127659574468]})

	# 	with self.assertRaises(ValueError):
	# 		response = self.client.post(
	# 			reverse('scikit_chart:regression_line'),
	# 			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
	# 			content_type='application/json',
	# 			data=data)

	def test_k_nearest_neighborns_view_invalid_request_method(self):
		response = self.client.get(reverse('scikit_chart:k_nearest_neighborns'))

		self.assertEqual(response.status_code, 404)
 
	def test_k_nearest_neighborns_view_valid_POST_request(self):
		data = json.dumps({
			'group_1_x': [-60.00820746914188, -45.58837174844149, -64.59918363153284,
						  -39.863115672632986, -38.4914142067621, -43.16638681450628,
						  -31.08237435797998, -51.806485151240835, -53.832322954258714,
						  -50.235370953453895, -41.146571279514994, -35.26809529798672,
						  -59.931199971447214, -68.30921926446172, -53.23710526087602,
						  -58.81454608184539, -84.12951983078082, -28.10747120361472,
						  -78.56689427079911, -42.98614966815097],
			'group_1_y': [19.282597178410875, -23.774421516143896, -6.974796768930782,
						  -15.19761970673579, -27.0154426912631, 16.25875725171742,
						  8.574042897378002, -15.551660281395, -33.63571849546378,
						  15.89400756950937, -33.3521919523494, 8.125034518575328,
						  10.523438315595449, -13.930567280855954, 5.399382528382642,
						  1.3867659198012579, -19.59841366677378, -2.1357919593439765,
						  -5.0150723987695, -6.4391494769003765],
			'group_2_x': [-2.346079089266301, -16.04160775399051, -15.123613644165454,
						  30.176596624629717, -5.196986653989682, -10.40746349316031,
						  13.803416718893104, -11.40613942609418, -7.785545669107868,
						  -2.979518842257404, -24.911834063463104, 23.85128262810828,
						  -31.35324011023956, -6.896890540331082, -8.554394810838023,
						  -25.0850957294113, 8.737825115953855, -13.576101028455033,
						  4.937933101964136, -11.615062485519164],
			'group_2_y': [14.432616174743316, -11.15528161101885, 8.11186353806148,
						  8.791732195726617, 29.22670399710524, -3.092729711283134,
						  2.338668327911049, -3.9599670465869377, 10.414847649820981,
						  17.545965798588828, 15.824181950368082, 16.846115038365934,
						  -9.068801793346221, -22.239487399353003, -5.752076088542847,
						  25.50331090404283, 16.010402549478457, -5.252754593155647,
						  28.85710739361083, 20.894390583149388],
			'group_3_x': [36.407961496280215, 32.7878344875971, -1.1177037798303289,
						  -5.4839998296885, 6.868375876624366, 15.31373988757193,
						  19.286037992881646, 49.643081725066494, 6.784768878622977,
						  40.32036256702625, 25.876171119217293, 39.787489865568794,
						  44.19536506539873, 11.880531258785751, 22.807177585291086,
						  40.304024119457374, 9.986024310322886, 39.330286337357585,
						  26.387298040562765, 40.451905009401585],
			'group_3_y': [-96.41140345587853, -77.01249620060943, -51.40254148067211,
						  -93.85796751130201, -99.77961183012638, -108.67300955083525,
						  -84.33960676676703, -60.0752530862743, -70.93365973935182,
						  -37.31296581937234, -67.2474007165757, -61.92188665068697,
						  -90.3156562562736, -84.13158976264988, -105.69291868419802,
						  -107.68023703431561, -65.15612967810792, -95.9170014584279,
						  -102.76257434283393, -54.78922802667509],
			'new_point': [-20.046082949308754, -50.63829787234043]
		})

		response = self.client.post(
			reverse('scikit_chart:k_nearest_neighborns'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			content_type='application/json',
			data=data)

		self.assertEqual(response.status_code, 200)
		self.assertIn('group', response.content.decode('utf-8'))
		self.assertIn('confidence', response.content.decode('utf-8'))
		self.assertEqual('application/json', response['Content-Type'])
		

	def test_k_nearest_neighborns_view_invalid_data_in_POST_request(self):
		data = json.dumps({
			'group_1_x': [-60.00820746914188, -45.58837174844149, -64.59918363153284],
			'group_1_y': [19.282597178410875, -23.774421516143896, -6.974796768930782],
			'group_2_x': [-2.346079089266301, -16.04160775399051, -15.123613644165454],
			'group_2_y': [14.432616174743316, -11.15528161101885, 8.11186353806148],
			'group_3_x': [36.407961496280215, 32.7878344875971, -1.1177037798303289],
			'group_3_y': [-96.41140345587853, -77.01249620060943, -51.40254148067211],
			'new_point': [-20.046082949308754, -50.63829787234043]
		})

		with self.assertRaisesRegexp(ValueError, 'Expected n_neighbors'):
			response = self.client.post(
				reverse('scikit_chart:k_nearest_neighborns'),
				HTTP_X_REQUESTED_WITH='XMLHttpRequest',
				content_type='application/json',
				data=data)
