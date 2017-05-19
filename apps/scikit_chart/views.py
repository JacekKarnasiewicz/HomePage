import json
from random import randrange

from sklearn import linear_model
from sklearn.datasets.samples_generator import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from django.http import Http404, JsonResponse
from django.shortcuts import render


def scikit_chart(request):
	X, _ = make_blobs(n_samples=60, centers=3, cluster_std=15, n_features=2, shuffle=False, center_box=(-85, 85))
	group_1, group_2, group_3 = [X[i:i+20] for i in range(0, 59, 20)]
	ctx = {'group_1': group_1.tolist(), 'group_2': group_2.tolist(), 'group_3': group_3.tolist()}
	return render(request, 'scikit_chart/home.html', ctx)


def regression_line(request):
	if request.method == 'POST' and request.is_ajax():
		data = json.loads(request.body.decode('utf-8'))

		reg = linear_model.LinearRegression()
		x_train, x_test, y_train, y_test = train_test_split(
			data['observations_x'],
			data['observations_y'],
			test_size=0.2,
			random_state=0)

		# Train model
		reg.fit([[i] for i in x_train], y_train)

		# y = ax + b
		a = reg.coef_[0]
		b = reg.intercept_

		new_line = [[x, a*x+b] for x in [-100, 100]]

		# Prediction/accuracy (1 is perfect)
		accuracy = reg.score([[x] for x in x_test], y_test)

		return JsonResponse({'regression_line': new_line, 'accuracy': str(accuracy)})
	raise Http404()


def k_nearest_neighborns(request):
	if request.method == 'POST' and request.is_ajax():
		data = json.loads(request.body.decode('utf-8'))

		knn = KNeighborsClassifier(n_neighbors=13)

		x = (list(zip(data['group_1_x'], data['group_1_y'])) +
			 list(zip(data['group_2_x'], data['group_2_y'])) +
			 list(zip(data['group_3_x'], data['group_3_y'])))
		y = ([0]*len(data['group_1_x']) +
			 [1]*len(data['group_2_x']) +
			 [2]*len(data['group_3_x']))

		# Train model
		knn.fit(x, y)

		# Making predictions
		group_predicion = knn.predict([data['new_point']])

		# Confidence of the new point
		confidence = knn.predict_proba([data['new_point']])[0]

		return JsonResponse({'group': str(group_predicion[0]), 'confidence': '{}%'.format(int(max(confidence)*100))})
	raise Http404()
