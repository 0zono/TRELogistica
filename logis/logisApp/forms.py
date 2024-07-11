from django import forms
from .models import Municipio, Urna, MaterialEleitoral, ZonaEleitoral, MunicipioZona

class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = ['nome']

class UrnaForm(forms.ModelForm):
    class Meta:
        model = Urna
        fields = ['modelo', 'bio', 'zona_eleitoral', 'qtd']

class MaterialEleitoralForm(forms.ModelForm):
    class Meta:
        model = MaterialEleitoral
        fields = ['nome', 'tipo', 'quantidade']

class ZonaEleitoralForm(forms.ModelForm):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(), required=True)

    class Meta:
        model = ZonaEleitoral
        fields = ['nome', 'qtdSecoes', 'qtdUrnasEstoque', 'municipio']

    def save(self, commit=True):
        zona = super().save(commit=False)
        if commit:
            zona.save()
            municipio = self.cleaned_data['municipio']
            MunicipioZona.objects.create(municipio=municipio, zona=zona)
        return zona

