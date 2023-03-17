diversificador_explanation = '''
<div style="text-align: justify;">
O diversificador é um relatório gerado pela XP que expõe a distribuição 
da carteira dos clientes, ou seja, por produto. Sendo assim, pode ser 
usado para analisar alocações e vencimentos, por exemplo. Sua avaliação 
é, sempre, baseada na posição do cliente no dia de referência do relatório.
</div>
'''

positivador_explanation = '''
<div style="text-align: justify;">
O positivador é o principal relatório usado como base na metrificação de 
captação e carteira dos clientes. Gerado pela XP, ele detalha toda a 
entrada de capital novo, em uma análise por cliente, sob uma ótica mensal, 
ou seja, ele fomenta uma análise de captação entre o início e o final do mês.
</div>
'''

captacao_explanation = '''
<div style="text-align: justify;">
O relatório de captação é gerado pela Inteligência da Fatorial, com base no 
positivador. Aqui, você pode ver o detalhamento, por cliente, dos números que 
aparecem no painel "Captação Líquida". Um detalhe é que aqui, diferente do 
positivador, são consideradas as transferências entre escritórios.
</div>
'''

roa_explanation = '''
<div style="text-align: justify;">
O relatório de ROA da empresa traz como resultado uma tabela contendo o ROA 
de cada assessor nos últimos 12 meses, no ano e no mês correntes. Seu resultado
indendepende de qual assessor está selecionado, uma vez que o relatório é
feito sempre com base em toda a empresa. 
</div>
'''

receitas_2022_explanation = '''
<div style="text-align: justify;">
O relatório de receitas tem como fim analisar os  resultados de 2022. 
Assim, ele conta com opções de filtragens relativas aos meses, aos 
assessores, e às verticiais. Seu resultado indendepende de qual assessor 
está selecionado, uma vez que o relatório é feito sempre com base em toda 
a empresa. 
</div>
'''

captacao_2022_explanation = '''
<div style="text-align: justify;">
O relatório de receitas tem como fim analisar os  resultados de 2022. 
Assim, ele conta com opções de filtragens relativas aos meses, aos 
assessores, e às verticiais. Seu resultado indendepende de qual assessor 
está selecionado, uma vez que o relatório é feito sempre com base em toda 
a empresa. 
</div>
'''

NPS_2022_explanation = '''
<div style="text-align: justify;">
O NPS é medido pela XP, disponível para a Fatorial através da plataforma 
Medallia. Com a ajuda do time de Performance, filtramos esses dados e desenvolvemos 
relatórios periódicos para metrificar a performance dos assessores. 
O seguinte relatório representa uma ótica anual. 
</div>
'''

in_progress_message = '''
<div>
Isso ainda está em desenvolvimento, estará disponível nos próximos dias.
</div>'''

exportacao_positivador = '''<b>Positivador</b>: Disponível em: XP Connect > Relatórios Gerenciais > Positivador'''

exportacao_transferecnias = '''<b>Transferências</b>: Disponível em: XP Connect > Cadastro > Transferência de Clientes > Acompanhamento > Filtrar Data'''

rotina_captacao_explanation = f'''
<div style="text-align: justify;">
A rotina de captação serve para consolidar os dados da XP relativos à entrada de novo
capital, com base no cruzamento de dados com os relatórios de transferência. Com isso,
as bases de dados que precisam ser exportadas são:
<ul>
<li> {exportacao_positivador} </li>
<li> {exportacao_transferecnias} </li>
</ul>

<p>
Ambos os relatórios devem ser salvos no dropbox, na pasta "Fatorial/Inteligência/Códigos/captacao_diario" 
com nomes "captacao_ddmmaa" e "transferencia_ddmmaa", em formato excel, sendo dd = dia, mm = mês e aa = ano, 
referentes emissão do relatório (exemplo: 06/01/2014 = 060114).
</p>
<p>Como uma boa prática, salve junto o diversificador, sempre. Esse deve ser armazenado na pasta "Fatorial > 
Inteligência > Codigos > COE > arquivos", com o mesmo formato de data identificando.
</p>
</div>
'''

rotina_aniversario_explanation = f'''
<div style="text-align: justify;">
Essa rotina não depende de nenhuma outra exportação de dados, podendo ser rodada sem nenhum input de planilha no Dropbox.
</div>
'''

rotina_ranking_explanation = f'''
<div style="text-align: justify;">
Para rodar essa rotina, é necessário que a rotina de cpatação seja executada antes, pois ela usa como base o relatório de captação.
</div>
'''

table_capture_link = '<a href="https://chrome.google.com/webstore/detail/table-capture/iebpjdmgckacbodjpijphcplhebcmeop?hl=de">Table Capture</a>'

rotina_COE_explanation = f'''
<div style="text-align: justify;">
<p>
Para rodar essa rotina, é necessário exportar os dados de produção de COE do Hub. Para isso, é
útil ter a extensão {table_capture_link} instalada no navegador. A tabela estará disponível em:
</p>
<p>
Hub > Produtos > COE > Central de Ordens > Primária (3ª Coluna).
</p>
<p>
Em seguida, deverá ser copiado o conteúdo e colado na planilha "COE_mes.xlsx", que estará no diretório
"Dropbox/Fatorial/Inteligência/Codigos/COE/Análise de COE".
</p>
</div>
'''

rotina_aviso_bases_B2C_explanation = f'''
<div style="text-align: justify;">
<p>
Essa rotina deve ser rodada sempre que for baixado um novo positivador, e ela deve, também, ser 
rodada posteriormente ao relatório de captação. Dito isso, é importante checar o e-mail inteligencia.fatorial@gmail.com, 
porque é por lá que respondem esse aviso.
</p>
<p>
Caso esse aviso tenha sido respondido, é necessário atualizar a planilha de distribuição de clientes, que está localizada em: 
"Fatorial/Inteligência/Codigos/Relatórios Digital/Base Clientes". O nome do arquivo é "distribuicao_clientes_MES_CELULA".
</div>
'''

rotina_aviso_bases_relatorio_carteira = f'''
<div style="text-align: justify;">
Para rodar essa rotina, é necessário que a rotina de cpatação seja executada antes, pois ela usa como base o relatório de captação.
</div>
'''

rotina_NPS = f'''
<div style="text-align: justify;">
Para rodar essa rotina, é necessário exportar uma série de relatórios do Medallia, e fazemos fazer upload deles aqui no sistema. 
<b>Os relatórios devem ter o upload feito nessa ordem, obrigatoriamente</b>:
<ul>
<li>NPS XP Assessoria > NPS Assessoria</li>
<li>NPS XP Onboarding > Ranking</li>
<li>Lista de envios > Envios</li>
<li>Lista de envios > Envios (filtrando Enviado pelo app? == Sim)</li>
<li>NPS XP Assessoria > Indicações</li>
<li>Lista de respostas >  Lista de Respostas</li>
<li>NPS XP Assessoria > Interesse em Previdência</li>
</ul>
<p>
Apenas o acesso da Louise tem a visão do NPS de todos os assessores. Para exportar os relatórios, é necessário <b>filtrar pelos últimos 30 dias</b>, usando o acesso dela. 
</p>
</div>
'''


