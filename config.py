from functions import Get, get_most_recent_data, get_most_recent_data_receita

# proportion
bar_height=500
columns_proportion=[5,3]
primary_color = '1D2843'
secondary_background_color = 'F1E2D2'
background_color = 'EFE5DC'
text_color = '11153D'


# groups
adms = ['Rodrigo Cabral', 'Jansen Costa', 'Leonardo Motta', 'Moises', 'Pablo Langenbach', 'Alexandre Pessanha', 'Louise Miranda']
team_jansen = ['Yago Meireles']
private = ['Renata Schneider']
exclusive = ['Soraya Brum', 'Alex Marinho']
digital = ['Bruna Krivochein', 'Pedro Aziz']

# lists
list_functions = ['Captação', 'Aniversário', 'Ranking Diário', 'COE', 'Avisos Bases B2C', 'Resumo Carteiras', 'Relatório NPS']
list_relatorios = ['Relatórios XP', 'Relatórios Inteligência']
list_relatorios_adm = ['Performance Geral']
landing_page_relatorios = ['Carteira','Captação', 'Receita']

#primary databases
captacao = Get.captacao_total()
receitas = Get.receitas_total()
carteiras = Get.carteira_total()
metas = Get.metas_2023()
positivador = None
contas_novas = Get.novos_transf_total()

# extras
most_recent_data = get_most_recent_data()
most_recent_receita = get_most_recent_data_receita(receitas)

assessores = Get.assessores()
suitability = Get.suitability()
clientes_rodrigo = Get.clientes_rodrigo()
