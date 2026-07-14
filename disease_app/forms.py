from django import forms
from django.conf import settings


class ImageUploadForm(forms.Form):
    """Form for uploading a leaf image for disease detection."""

    image = forms.ImageField(
        label='Leaf Image',
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/jpeg,image/jpg,image/png',
            'id':     'image-input',
            'class':  'd-none',
        }),
        error_messages={
            'required': 'Please select an image to upload.',
            'invalid_image': 'The uploaded file is not a valid image.',
        }
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('No image file received.')

        # Validate content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if hasattr(image, 'content_type') and image.content_type not in allowed_types:
            raise forms.ValidationError(
                f'Unsupported file type: {image.content_type}. '
                'Please upload a JPG or PNG image.'
            )

        # Validate file size
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if image.size > max_size:
            raise forms.ValidationError(
                f'Image file too large ({image.size / 1024 / 1024:.1f} MB). '
                f'Maximum allowed size is {max_size / 1024 / 1024:.0f} MB.'
            )

        return image
