"""
See https://docs.djangoproject.com/en/dev/topics/forms/ for details.
"""
from django import forms


class LoginForm(forms.Form):
	"""
		Login Form used to show login fields in GraphSpace webpages.
		This form is located within the top navbar.
	"""

	# attrs to specify extra html attributes
	user_id = forms.CharField(max_length=100, label='User ID', required=False, widget=forms.TextInput(
		attrs={
			'placeholder': 'Email',
			'class': 'form-control',
			'size': '13',
			'id': 'email'
		}))

	pw = forms.CharField(required=False, label='Password', widget=forms.PasswordInput(
		attrs={
			'placeholder': 'Password',
			'class': 'form-control',
			'size': '13',
			'id': 'pw'
		}))


class RegisterForm(forms.Form):
	"""
		Register form to help create an account for a new user.
	"""

	user_id = forms.CharField(required=False, label='Email', max_length=100,
				widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'size': '25', 'id': 'user_id'}))
	password = forms.CharField(required=False, label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'size': '25', 'id': 'password'}))
	verify_password = forms.CharField(required=False, label='Verify Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'size': '25', 'id': 'verify_password'}))

	def clean(self):
		"""
			Form validation to check if two passwords provided are
			equivalent.

			https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-a-specific-field-attribute
		"""
		cleaned_data = super(RegisterForm, self).clean()
		pw = cleaned_data.get("password")
		vpw = cleaned_data.get("verify_password")

		if pw and vpw:
			if pw != vpw:
				raise forms.ValidationError("Passwords do not match.")

		return cleaned_data
