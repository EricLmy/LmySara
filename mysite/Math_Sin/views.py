from django.shortcuts import render
from django.http import HttpResponse

from matplotlib.backends.backend_webagg_core import FigureManagerWebAgg, new_figure_manager_given_figure
from matplotlib.figure import Figure
import numpy as np 

# Create your views here.
def index1(request):
	return HttpResponse("Hello, 微量元素.")

def create_figure():
	fig = Figure()
	a = fig.add_subplot(111)
	t = np.arange(0.0, 3.0, 0.01)
	s = np.sin(2 * np.pi * t)
	a.plot(t, s)
	return fig

def index(request):
	figure = create_figure()
	manager = new_figure_manager_given_figure(id(figure), figure)
	context = {'ws_uri':"/Math_Sin/",'fig_id': manager.num}
	print("--------------")
	print(request)
	print("--------------")
	return render(request, 'Math_Sin/index.html', context)

