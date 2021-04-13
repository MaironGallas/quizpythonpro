from django.shortcuts import render, redirect

# Create your views here.
from quiz.base.forms import AlunoForm
from quiz.base.models import Pergunta


def home(request):
    if request.method == 'POST':
        formulario = AlunoForm(request.POST)
        if formulario.is_valid():
            aluno = formulario.save()
            return redirect('/perguntas/1')
    return render(request, 'base/home.html')

def perguntas(request, indice):
    pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
    context = {'indice_da_questao': indice, 'pergunta': pergunta}
    return render(request, 'base/game.html', context=context)

def classificacao(request):
    return render(request, 'base/classificacao.html')
