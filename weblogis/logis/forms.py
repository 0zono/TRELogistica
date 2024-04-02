from django import forms
from .models import Municipios
from .models import ZE

class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipios
        fields = '__all__'  # Use '__all__' para incluir todos os campos do modelo no formulário

class ZEForm(forms.ModelForm):
    class Meta:
        model = ZE
        fields = '__all__'