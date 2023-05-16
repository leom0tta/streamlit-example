from imports import pd, datetime, st, go, make_subplots

from functions import to_excel, get_meses
from config import most_recent_data, adms, receitas, captacao, assessores, private, exclusive, digital, team_jansen

def app(name, captacao=captacao, receitas=receitas, assessores=assessores):

    month = get_meses()

    dict_month = pd.DataFrame( [[ month[i] , j, datetime.datetime(2000 + j, i+1, 1).strftime("%Y - %m")] for i in range(12) for j in [22,23,24]] , columns = ['Mes', 'Ano', 'Month'])

    receitas = receitas.merge(dict_month, how='left', on=['Mes', 'Ano'])
    captacao = captacao.merge(dict_month, how='left', on=['Mes', 'Ano'])

    captacao = captacao.sort_values(['Month'], ascending=False)

    periodos = captacao['Month'].drop_duplicates().head(12)

    captacao = captacao.loc[ (captacao['Month'].isin(periodos))]
    receitas = receitas.loc[ (receitas['Month'].isin(periodos))]

    median_company_array = [captacao['Captação Líquida'].median() for i in range(12)]

    # header

    st.write("""
    # Captação Líquida
    """)

    if name in adms:
        nomes_filtrados = st.multiselect('Assessor', ['Fatorial'] + ['Fatorial'] + assessores['Nome assessor'].drop_duplicates().fillna(assessores['Código assessor']).sort_values().to_list(), 'Fatorial')

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

    if not nomes_filtrados == ['Fatorial']:
        receitas = receitas[ receitas['Nome assessor'].isin(nomes_filtrados) ]
        captacao = captacao[ captacao['Nome assessor'].isin(nomes_filtrados) ]

    # carteira + receita
    carteira = captacao.groupby('Month').sum()[['Net Em M']]
    carteira.columns = ['Carteira']
    resumo_receita = receitas.groupby('Month').sum()[['Receita']]
    resumo_receita['Receita Acumulada'] = resumo_receita['Receita'].cumsum()
    resumo_receita = resumo_receita.merge(carteira, how='left', left_index=True, right_index=True)
    resumo_receita['ROA'] = resumo_receita['Receita'] / resumo_receita['Carteira'] * 12

    try:
        roa = sum(resumo_receita['Receita']) / sum(resumo_receita['Carteira']) * 12
    except ZeroDivisionError:
        roa = 0

    # captacao

    captacao_filt = captacao.copy()

    # captacao

    resumo_captacao = captacao.groupby('Month').sum()[['Captação Líquida', 'Net Em M']]
    resumo_captacao.rename(columns={'Net Em M' : 'Carteira'}, inplace=True)
    #resumo_captacao['Captação Acumulada'] = resumo_captacao['Captação Líquida'].cumsum()
    resumo_captacao = resumo_captacao[['Captação Líquida', 'Carteira']]
    resumo_captacao = resumo_captacao.merge(resumo_receita[['ROA']], how='left', left_index=True, right_index=True)

    acumulado_2023 = resumo_captacao.loc[['2023' in idx for idx in resumo_captacao.index], 'Captação Líquida'].sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    ultimo_mes_fechado = int(resumo_captacao.index[-1][-2::])
    ultimo_mes_fechado = month[ultimo_mes_fechado-1]

    col1.metric(f"Captação {ultimo_mes_fechado} (até {most_recent_data[0:2]}/{most_recent_data[2:4]}/{most_recent_data[4:]})", 'R$ {:,.2f}'.format(sum(resumo_captacao['Captação Líquida'].tail(1))))
    col2.metric("Média Móvel 3 meses", 'R$ {:,.2f}'.format(sum(resumo_captacao['Captação Líquida'].tail(3))/3))
    col3.metric("Captação Acumulada 2023", 'R$ {:,.2f}'.format(acumulado_2023))
    col4.metric("Meta Mensal", 'R$ {:,.2f}'.format(3e6))
    col5.metric("Meta Anual", 'R$ {:,.2f}'.format(3e6*12))

    mean_assessor_array = [captacao_filt['Captação Líquida'].mean() for i in captacao_filt]

    exporting_file_cap = resumo_captacao.copy()

    fig = make_subplots(specs=[[{"secondary_y": True}]], row_heights=[450])

    fig.add_trace(go.Bar(x=resumo_captacao.index, y=resumo_captacao['Captação Líquida'], name='Captação', yaxis='y', width = 0.5))

    fig.add_trace(go.Scatter(x=resumo_captacao.index, y=mean_assessor_array, name='Média Assessor', mode='lines', line=dict(width=2, dash='dot')))

    fig.update_traces(selector=dict(name='Captação'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',)
                  #marker_line_width=1.5, opacity=.96)
    
    fig.update_traces(selector=dict(name='Média Assessor'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',)
                  #marker_line_width=1.5, opacity=.96)
    
    resumo_captacao['ROA'] = resumo_captacao['ROA']*100

    col1, col2 = st.columns([2.5,1])
    
    col1.plotly_chart(fig, use_container_width=True)

    col2.write(resumo_captacao.style.format({'Carteira':'R$ {:,.2f}', 'Captação Líquida':'R$ {:,.2f}', 'ROA':'{:,.3f} %'}))

    df = to_excel(exporting_file_cap)

    col2.download_button(
        label='Exportar Captação',
        data = df,
        file_name = f'Captacao 2022.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )