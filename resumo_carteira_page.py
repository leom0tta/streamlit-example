import streamlit as st
from imports import  go

from functions import to_excel, get_meses, get_cod_data, get_last_month
from functions import ResumoCarteira, Get, Data

from config import adms, private, exclusive, digital, team_jansen
from config import assessores, suitability, clientes_rodrigo
from config import most_recent_data, most_recent_receita

def app(name, most_recent_data = most_recent_data):

    mes = Data(most_recent_data).text_month
    year = Data(most_recent_data).year
    
    cod_mes_1 = get_last_month(most_recent_data)
    mes_1 = most_recent_receita[0]
    year_1 = most_recent_receita[1]
    # header

    st.write("""
    # KPI\'s da Carteira XP
    """)

    if name in adms:
        nomes_filtrados = st.multiselect('Assessor', ['Fatorial'] + assessores['Nome assessor'].drop_duplicates().fillna(assessores['Código assessor']).sort_values().to_list(), 'Fatorial')

    elif name in team_jansen:
        nomes_filtrados = st.multiselect('Assessor', [name] + ['Jansen Costa', 'Private'], name)
    
    elif name in private:
        nomes_filtrados = st.multiselect('Assessor', [name] + ['Private'], name)
    
    elif name in exclusive:
        nomes_filtrados = st.multiselect('Assessor', [name] + ['Exclusive', 'Atendimento Fatorial'], name)

    elif name in digital:
        nomes_filtrados = st.multiselect('Assessor', [name] + ['Atendimento Fatorial'], name)
    
    else:
        nomes_filtrados = [name]

    with st.spinner('Um momento...'):

        posi = Get.captacao(most_recent_data, sheet_name='Positivador M')

        if not nomes_filtrados == ['Fatorial']:
            cod_filtrados = assessores.loc[assessores['Nome assessor'].isin(nomes_filtrados), 'Código assessor'].to_list()
            posi = posi[posi['Assessor'].isin(cod_filtrados)]

        resumo_carteira, capt_mes, receita_mes = ResumoCarteira.get_resumo(posi,assessores, suitability, clientes_rodrigo, nomes_filtrados)

    carteira = sum(resumo_carteira['Net Em M'].fillna(0))
    qtd_clientes = len(resumo_carteira.loc[resumo_carteira['Status'].isin(['ATIVO', 'INATIVO']),'Cliente'])
    captacao = sum(resumo_carteira[f'Captação {mes} {year}'].fillna(0))
    captacao_12 = sum(resumo_carteira[f'Captação 12 meses'].fillna(0))
    receita = sum(resumo_carteira[f'Receita {mes_1} {year_1}'].fillna(0))
    receita_12 = sum(resumo_carteira['Receitas 12 meses'].fillna(0))

    try:
        roa = receita/carteira*12
        roa_12 = receita_12/carteira
    except ZeroDivisionError:
        roa = 0
        roa_12 = 0

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Patrimônio Líquido", 'R$ {:,.2f}'.format( carteira) )
    col1.metric("Quantidade de Clientes", '{:,.0f}'.format( qtd_clientes ))
    
    col2.metric(f"Captação da Base em {mes}", 'R$ {:,.2f}'.format( captacao ) )
    col2.metric("Potêncial Histórico de Captação - 12 meses", 'R$ {:,.2f}'.format( captacao_12) )
    
    col3.metric(f"Receita da Base em {mes_1}", 'R$ {:,.2f}'.format( receita) )
    col3.metric("Potêncial Histórico de Receita - 12 meses", 'R$ {:,.2f}'.format( receita_12) )
    
    col4.metric(f"ROA em {mes_1}", '{:,.3f}%'.format( roa*100 ))
    col4.metric(f"ROA 12 meses", '{:,.3f}%'.format( roa_12*100) )

    col1, col2 = st.columns(2)

    fig_1 = go.Figure()
    fig_1.add_trace(go.Bar(x=capt_mes['Month'], y=capt_mes['Captação Líquida em M'], name='Captação', width = 0.5))
    fig_1.update_traces(selector=dict(name='Captação'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)
    fig_1.update_layout(title='<b>Captação Histórica da Base</b>', barmode='stack',
                          title_x=0.5, title_font_size=20)

    col1.plotly_chart(fig_1, use_container_width=True)

    fig_2 = go.Figure()
    fig_2.add_trace(go.Bar(x=receita_mes['Month'], y=receita_mes['Valor Bruto Recebido'], name='Receita', width = 0.5))
    fig_2.update_traces(selector=dict(name='Receita'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)
    fig_2.update_layout(title='<b>Receita Histórica da Base</b>', barmode='stack',
                          title_x=0.5, title_font_size=20)
    
    col2.plotly_chart(fig_2, use_container_width=True)



    st.write('### Resumo por Cliente')

    display_resumo_carteira = resumo_carteira.copy()

    for i in [f'ROA {mes_1} {year_1}', f'ROA 12 meses']:
        display_resumo_carteira[i] *= 100

    st.write(display_resumo_carteira.style.format({'Captação 12 meses':'R$ {:,.2f}', 'Net Em M':'R$ {:,.2f}',
                                                   f'Captação {mes} {year}':'R$ {:,.2f}', f'Receita {mes_1} {year_1}':'R$ {:,.2f}',
                                                    'Receitas 12 meses':'R$ {:,.2f}', 'ROA 12 meses':'{:,.3f} %',
                                                      f'ROA {mes_1} {year_1}':'{:,.3f} %'}))

    xlsx_bytes = to_excel(resumo_carteira)

    st.download_button('Baixar o Relatório completo', xlsx_bytes, f'Resumo_Carteira_{nomes_filtrados}.xlsx')




