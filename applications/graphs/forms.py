"""
See https://docs.djangoproject.com/en/dev/topics/forms/ for details.
"""
from django import forms


class SearchForm(forms.Form):
	"""
		Search form used to perform search on GraphSpace
	"""

	def __init__(self, *args, **kwargs):
		"""
			Initialize the form. A keyword argument 'placeholder' may be
			given.

			This can be customized to specify additional parameters if it
			needs to.
		"""
		if 'placeholder' in kwargs:
			self.placeholder = kwargs.pop('placeholder')
			# must be called after 'placeholder' is popped from kwargs
			super(SearchForm, self).__init__(*args, **kwargs)
			self.fields['search'].widget = forms.TextInput(attrs={'placeholder': self.placeholder, 'class': 'form-control', 'type': 'text', 'name': 'search'})
		else:
			super(SearchForm, self).__init__(*args, **kwargs)
			self.fields['search'].widget = forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'name': 'search'})

	search = forms.CharField(required=False, label='', max_length=100)
