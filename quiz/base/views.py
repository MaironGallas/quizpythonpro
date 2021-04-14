from django.db.models import Sum
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.timezone import now

from quiz.base.forms import AlunoForm
from quiz.base.models import Pergunta, Aluno, Resposta


def home(request):
    if request.method == 'POST':
        #Usuário já existe
        email = request.POST['email']
        try:
            aluno = Aluno.objects.get(email=email)
        except Aluno.DoesNotExist:
            #Usuário não existe
            formulario = AlunoForm(request.POST)
            if formulario.is_valid():
                aluno = formulario.save()
                request.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                context = {'formulario': formulario}
                return render(request, 'base/home.html', context)
        else:
            request.session['aluno_id'] = aluno.id
            return redirect('/perguntas/1')

    return render(request, 'base/home.html')

PONTUACAO_MAXIMA = 1000
def perguntas(request, indice):
    try:
        aluno_id = request.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        try:
            pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
        except IndexError:
            return redirect('/classificacao')
        else:
            context = {'indice_da_questao': indice, 'pergunta': pergunta}
            if request.method == 'POST':
                resposta_indice = int(request.POST['resposta_indice'])
                if resposta_indice == pergunta.alternativa_correta:
                    #Armazenar Dados da Resposta
                    try:
                        data_da_primeira_resposta = Resposta.objects.filter(pergunta=pergunta).order_by('respondida_em')[0].respondida_em
                    except IndexError:
                        Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=PONTUACAO_MAXIMA).save()
                    else:
                        diferenca = now() - data_da_primeira_resposta
                        diferenca_em_segundos = int(diferenca.total_seconds())
                        pontos = max(PONTUACAO_MAXIMA - diferenca_em_segundos, 10)
                        Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=pontos).save()
                    return redirect(f'/perguntas/{indice + 1}')
                context['resposta_indice'] = resposta_indice
            return render(request, 'base/game.html', context=context)

def classificacao(request):
    try:
        aluno_id = request.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        pontos_dict = Resposta.objects.filter(aluno_id=aluno_id).aggregate(Sum('pontos'))
        pontuacao_do_aluno = pontos_dict['pontos__sum']

        numero_de_alunos_com_maior_pontuacao = Resposta.objects.values('aluno').annotate(Sum('pontos')).filter(pontos__sum__gt = pontuacao_do_aluno).count()
        primeiros_alunos_da_classificacao = list(
            Resposta.objects.values('aluno', 'aluno__nome').annotate(Sum('pontos')).order_by('-pontos__sum')[:5]
        )
        context = {'pontuacao_do_aluno': pontuacao_do_aluno,
                   'posicacao_do_aluno': numero_de_alunos_com_maior_pontuacao + 1,
                   'primeiros_alunos_da_classificacao': primeiros_alunos_da_classificacao}
        return render(request, 'base/classificacao.html', context)
