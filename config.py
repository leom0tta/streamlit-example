from functions import Get, get_most_recent_data_receita, get_most_recent_data

# proportion
bar_height=500
columns_proportion=[5,3]
primary_color = '1D2843'
secondary_background_color = 'F1E2D2'
background_color = 'FCECDC'
text_color = 'FCE5CD'


# groups
adms = ['Rodrigo Cabral', 'Marcio Murad', 'Jansen Costa', 'Pablo Langenbach',               # sócios
        'Leonardo Motta', 'Moises', 'Alexandre Pessanha', 'Louise Miranda',  'Paulo Minor'  # adm
        'Rodolfo', 'Lucas Mattoso', 'Eduardo Santos'                                        # mesa rv
        ]                                        
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

#fluid_databases
diversificador = Get.diversificador(most_recent_data)
saldos = Get.saldos()

# bases dados
assessores = Get.assessores()
assessores = assessores.loc[assessores['Time'].isin(['B2B','B2C','Outros','Mesa RV'])]
suitability = Get.suitability()
clientes_rodrigo = Get.clientes_rodrigo()
