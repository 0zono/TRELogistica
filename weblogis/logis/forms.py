from django import forms
from .models import Municipios, ZE, Secao


class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipios
        fields = ['nome', 'KM_Cuiaba', 'muni_id', 'sede', 'zona_eleitoral']


class ZEForm(forms.ModelForm):
    class Meta:
        model = ZE
        fields = '__all__'

class secaoForm(forms.ModelForm):
    class Meta:
        model = Secao
        fields = '__all__'