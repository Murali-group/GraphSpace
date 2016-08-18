'''
See https://docs.djangoproject.com/en/dev/topics/forms/ for details.
'''

from django import forms
from graphs_old.util import db

class LoginForm(forms.Form):
	'''
		Login Form used to show login fields in GraphSpace webpages. 
		This form is located within the top navbar.
	'''

	# attrs to specify extra html attributes
	user_id = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control', 'size': '13', 'id': 'email'}))
	pw = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control', 'size': '13', 'id': 'pw'}))

class SearchForm(forms.Form):
	'''
		Search form used to perform search on GraphSpace
	'''

	def __init__(self, *args, **kwargs):
		'''
			Initialize the form. A keyword argument 'placeholder' may be 
			given.

			This can be customized to specify additional parameters if it 
			needs to. 
		'''
		if 'placeholder' in kwargs:
			self.placeholder = kwargs.pop('placeholder')
			# must be called after 'placeholder' is popped from kwargs
			super(SearchForm, self).__init__(*args, **kwargs)
			self.fields['search'].widget = forms.TextInput(attrs={'placeholder': self.placeholder, 'class': 'form-control', 'type': 'text', 'name': 'search'})
		else:
			super(SearchForm, self).__init__(*args, **kwargs)
			self.fields['search'].widget = forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'name': 'search'})
	
	search = forms.CharField(required=False, label='', max_length=100)

class RegisterForm(forms.Form):
	'''
		Register form to help create an account for a new user.
	'''

	user_id = forms.CharField(required=False, label='Email', max_length=100,
				widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'size': '25', 'id': 'user_id'}))
	password = forms.CharField(required=False, label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'size': '25', 'id': 'password'}))
	verify_password = forms.CharField(required=False, label='Verify Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'size': '25', 'id': 'verify_password'}))

	def clean_user_id(self):
		'''
			Form validation to check if the user id already exist
			in the database.

			https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-a-specific-field-attribute
		'''
		cleaned_data = super(RegisterForm, self).clean()
		user_id = cleaned_data["user_id"]

		check_user = db.emailExists(user_id)

		if check_user == None:
			return user_id
		else:
			return None

	def clean(self):
		'''
			Form validation to check if two passwords provided are 
			equivalent.

			https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-a-specific-field-attribute
		'''
		cleaned_data = super(RegisterForm, self).clean()
		pw = cleaned_data.get("password")
		vpw = cleaned_data.get("verify_password")

		if pw and vpw:
			if pw != vpw:
				raise forms.ValidationError("Passwords do not match.")

		return cleaned_data