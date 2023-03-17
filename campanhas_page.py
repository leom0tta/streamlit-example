from imports import pd, datetime, st, go, make_subplots

from functions import to_excel, get_meses, espacamento
from config import adms, receitas, captacao
from config import private, exclusive, digital, team_jansen
from config import most_recent_receita

def app(name, captacao=captacao, receitas=receitas, most_recent_receita=most_recent_receita):

    df_rules = pd.DataFrame({
        'Categoria': [f'Categoria {i}' for i in ['A','B','C','D','E','F','G']],
        'Captação Líquida': [6e6,6e6,12e6,12e6,12e6,18e6,18e6],
        'ROA':[0.0035,0.0050,0.0035,0.0050,0.0070,0.0050,0.0070],
        'Bônus':[0.0010,0.0015,0.0015,0.0020,0.0025,0.0025,0.0030]
        })
    
    semesters_months = [f'2023 - 0{i+1}' for i in range(6)]

    month = get_meses()

    dict_month = pd.DataFrame( [[ month[i] , j, datetime.datetime(2000 + j, i+1, 1).strftime("%Y - %m")] for i in range(12) for j in [22,23,24]] , columns = ['Mes', 'Ano', 'Month'])

    receitas = receitas.merge(dict_month, how='left', on=['Mes', 'Ano'])
    captacao = captacao.merge(dict_month, how='left', on=['Mes', 'Ano'])

    captacao = captacao.sort_values(['Month'], ascending=False)

    periodos = [23]

    captacao = captacao.loc[ (captacao['Ano'].isin(periodos))]
    receitas = receitas.loc[ (receitas['Ano'].isin(periodos))]

    # header

    st.write("""
    # CFA - Campanha de Captação e ROA
    """)

    if name in adms:
        nomes_filtrados = st.multiselect('Assessor', ['Fatorial'] + captacao['Nome assessor'].drop_duplicates().fillna(captacao['Código assessor']).sort_values().to_list(), 'Fatorial')

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
    resumo_captacao = resumo_captacao[['Captação Líquida', 'Carteira']]
    resumo_captacao = resumo_captacao.merge(resumo_receita[['Receita','ROA']], how='left', left_index=True, right_index=True)

    ultimo_mes_fechado = int(resumo_captacao.index[-1][-2::])
    ultimo_mes_fechado = month[ultimo_mes_fechado-1]

    # separa os grandes números

    captacao_acumulada = sum(resumo_captacao['Captação Líquida'])
    roa_acumulado = resumo_receita['ROA'].mean()

    # Calcula as projeções

    n_meses = len(resumo_captacao.index)
    n_meses_restantes = 6 - n_meses

    df_rules['Captação Líquida Ajustada'] = df_rules['Captação Líquida']*n_meses/6

    mask_elegible = (df_rules['Captação Líquida Ajustada'] < captacao_acumulada) & (df_rules['ROA'] < roa_acumulado)

    categorie = df_rules.loc[mask_elegible].tail(1)
    next_categorie = df_rules.loc[~mask_elegible, 'Categoria'].head(1).index[0]

    col1, col2 = st.columns([1,4])

    categoria = col1.selectbox(label='Categoria de Parâmetro',options=df_rules['Categoria'], index=int(next_categorie))

    try:
        current_categorie = categorie['Categoria'].iloc[-1]
        current_bonus = categorie['Bônus'].iloc[-1] * categorie['Captação Líquida'].iloc[-1]
        current_bonus = 'R$ {:,.2f}'.format(current_bonus)
    
        espacamento(1,col2)
        col2.markdown(f'''
        <div style="text-align: center;">
        <font size="5">
        Você está na <b>{current_categorie}</b>, com bônus mínimo de <b>{current_bonus}</b>
        </font>
        </div>
        ''', unsafe_allow_html=True)
    except:
        col2.markdown(f'#### Você ainda não está elegível em nenhuma categoria.')
    aspiring_categorie = df_rules.loc[df_rules['Categoria'] == categoria]
    
    # capt
    min_capt_subir = (sum(aspiring_categorie['Captação Líquida']) - captacao_acumulada)/n_meses_restantes
    meses_restantes = semesters_months[n_meses_restantes::]

    # roa
    min_roa_subir = (sum(aspiring_categorie['ROA']) - roa_acumulado)
    
    if min_roa_subir < 0:
        min_roa_subir = 'ROA > min da próxima categoria'
    else:
        min_roa_subir = '{:,.3f} %'.format(min_roa_subir*100)
    

    exporting_file_cap = resumo_captacao.copy()

    # Faz o plot captação

    fig = make_subplots(specs=[[{"secondary_y": True}]], row_heights=[450])

    fig.add_trace(go.Bar(x=resumo_captacao.index, y=resumo_captacao['Captação Líquida'], name='Captação', yaxis='y', width = 0.5))

    fig.add_trace(go.Bar(x=meses_restantes, y=[min_capt_subir for i in meses_restantes], name='Projeção para subir de Categoria', yaxis='y', width = 0.5, marker_pattern_shape="/"))

    median_assessor_array = [captacao_filt['Captação Líquida'].median() for i in semesters_months]

    fig.add_trace(go.Scatter(x=semesters_months, y=median_assessor_array, name='Mediana Assessor', mode='lines', line=dict(width=2, dash='dot')))

    fig.update_traces(selector=dict(name='Captação'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)

    fig.update_traces(selector=dict(name='Projeção para subir de Categoria'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',
                  marker_line_width=1.5, opacity=.96)
    
    fig.update_traces(selector=dict(name='Mediana Assessor'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',
                  marker_line_width=1.5, opacity=.96)
    
    fig.update_layout(title='<b>Projeção de Captação na Campanha</b>', barmode='stack',
                          title_x=0.5, title_font_size=20)
    
    # receita
    n_meses = len(resumo_receita)
    n_meses_restantes = 6 - n_meses
    meses_restantes = semesters_months[n_meses::]

    receita_semestre_prox_etapa = (sum(aspiring_categorie['ROA'])*sum(resumo_captacao['Carteira'].tail(1))/12) * 6
    receita_restante = receita_semestre_prox_etapa - sum(resumo_receita['Receita'])
    min_receita_prox_etapa = receita_restante/n_meses_restantes

    receita_mediana = resumo_receita['Receita'].median()

    if (min_receita_prox_etapa - receita_mediana) < 0:
        min_receita_subir = 'Mediana > min da próxima categoria'
    else:
        min_receita_subir = '{:,.1f} %'.format(100*(min_receita_prox_etapa - receita_mediana)/receita_mediana)
    
    # Faz o plot receita

    fig_2 = make_subplots(specs=[[{"secondary_y": True}]], row_heights=[450])

    fig_2.add_trace(go.Bar(x=resumo_receita.index, y=resumo_receita['Receita'], name='Receita', yaxis='y', width = 0.5))

    fig_2.add_trace(go.Bar(x=meses_restantes, y=[min_receita_prox_etapa for i in meses_restantes], name='Projeção para subir de Categoria', yaxis='y', width = 0.5, marker_pattern_shape="/"))

    median_assessor_array_receita = [receita_mediana for i in semesters_months]

    fig_2.add_trace(go.Scatter(x=semesters_months, y=median_assessor_array_receita, name='Mediana Assessor', mode='lines', line=dict(width=2, dash='dot')))

    fig_2.update_traces(selector=dict(name='Receita'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)

    fig_2.update_traces(selector=dict(name='Projeção para subir de Categoria'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',
                  marker_line_width=1.5, opacity=.96)
    
    fig_2.update_traces(selector=dict(name='Mediana Assessor'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',
                  marker_line_width=1.5, opacity=.96)
    
    fig_2.update_layout(title='<b>Projeção de Receita na Campanha</b>', barmode='stack',
                          title_x=0.5, title_font_size=20)

    # Prepara o dataframe de regras

    display_df_rules = df_rules.copy()

    del display_df_rules['Captação Líquida Ajustada']

    display_df_rules.columns = ['Categoria', 'Captação min.', 'ROA min.', 'Bônus']

    display_df_rules['ROA min.'] *= 100
    display_df_rules['Bônus'] *= 100
    
    display_df_rules.set_index('Categoria', inplace=True)

    display_df_rules= display_df_rules.style.format({'Captação min.':'R$ {:,.2f}', 'Bônus':'{:,.3f} %', 'ROA min.':'{:,.3f} %'})
    
    try:
        def highlight_index(index_value):
            if index_value == current_categorie:
                return 'background-color: yellow'
            else:
                return ''
        display_df_rules = display_df_rules.applymap(highlight_index, subset=pd.IndexSlice[:, :])
    except:
        pass
    # Cards com dados
    col1, col2, col3, col4, col5 = st.columns(5)

    if min_capt_subir > median_assessor_array[0]:
        delta_capt = '{:,.1f} %'.format((min_capt_subir - median_assessor_array[0])/median_assessor_array[0]*100)
    else:
        delta_capt = 'Mediana > min da próxima categoria'
    col1.metric(f"Captação Mensal para a Próxima Categoria", 'R$ {:,.2f}'.format(min_capt_subir), delta=delta_capt)
    col2.metric("Captação Acumulada Semestre", 'R$ {:,.2f}'.format(captacao_acumulada))
    col3.metric('Receita Mensal para a Próxima Categoria', 'R$ {:,.2f}'.format(min_receita_prox_etapa), delta=min_receita_subir)
    col4.metric("ROA Acumulado", '{:,.3f} %'.format(100*roa_acumulado))
    col5.metric('ROA da Próxima Categoria', '{:,.3f} %'.format(100*sum(aspiring_categorie['ROA'])), delta=min_roa_subir)

    # plot + graficos

    resumo_captacao['ROA'] *= 100

    col1, col2 = st.columns([2,1])
    
    col1.plotly_chart(fig, use_container_width=True)

    col1.plotly_chart(fig_2, use_container_width=True)

    col2.write(resumo_captacao.style.format({'Carteira':'R$ {:,.2f}', 'Receita':'R$ {:,.2f}', 'Captação Líquida':'R$ {:,.2f}', 'ROA':'{:,.3f} %'}))

    df = to_excel(exporting_file_cap)

    col2.download_button(
        label='Exportar Captação',
        data = df,
        file_name = f'Captação 2022.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    col2.write(display_df_rules)