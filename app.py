from imports import st

st.set_page_config(page_title= 'Fatorial Assessores' ,page_icon = '',layout='wide')

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import captacao_page
import receita_page
import aniversario_page
import authenticator_page
import super_ranking_page
import rotinas_leo_page
import relatorios_page
import landing_page
import resumo_carteira_page
import vencimentos_page
import campanhas_page

from config import adms
from multipage import MultiApp

name, authentication_status, username, authenticator = authenticator_page.app()

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == True:
    
    apps = MultiApp()

    apps.add_app('Página Inicial', landing_page.app, name)
    apps.add_app('Captação Líquida', captacao_page.app, name)
    apps.add_app('Receita Bruta', receita_page.app, name)
    apps.add_app('Super Ranking', super_ranking_page.app, name)
    apps.add_app('Aniversário de Clientes', aniversario_page.app, name)
    apps.add_app('Vencimentos de Renda Fixa', vencimentos_page.app, name)
    apps.add_app('KPI\'s da Carteira XP', resumo_carteira_page.app, name)
    #apps.add_app('Campanha CFA', campanhas_page.app, name)
    apps.add_app('Relatórios', relatorios_page.app, name)

    if name in adms:
        apps.add_app('Rotinas Leo', rotinas_leo_page.app, name)

    apps.run()

    authenticator.logout("Logout", 'sidebar')

