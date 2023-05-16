from imports import st, px, pd, datetime, go
from imports import make_subplots

from functions import espacamento, to_excel, get_meses
from config import assessores, metas, adms, receitas, assessores, captacao, carteiras, private, exclusive, digital, team_jansen

def app(name, receitas=receitas, captacao=captacao, carteiras=carteiras, assessores = assessores):

    # header

    st.write("""
    # Receita Bruta
    """)

    espacamento(2,st) 

    # FILTRA PELOS 12 ÚLTIMOS MESES

    month = get_meses()

    dict_month = pd.DataFrame( [[ month[i] , j, datetime.datetime(2000 + j, i+1, 1).strftime("%Y - %m")] for i in range(12) for j in [22,23,24]] , columns = ['Mes', 'Ano', 'Month'])
    
    receitas = receitas.merge(dict_month, how='left', on=['Mes', 'Ano'])
    captacao = captacao.merge(dict_month, how='left', on=['Mes', 'Ano'])
    carteiras = carteiras.merge(dict_month, how='left', on=['Mes', 'Ano'])

    receitas = receitas.sort_values(['Month'], ascending=False)
    periodos = receitas['Month'].drop_duplicates().head(12)

    captacao = captacao.loc[ (captacao['Month'].isin(periodos))]
    receitas = receitas.loc[ (receitas['Month'].isin(periodos))]
    carteiras = carteiras.loc[ (carteiras['Month'].isin(periodos))]

    # SEGMENTAÇÃO DE USUÁRIO

    # content

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

    # dados medios Fatorial

    receita_produto_mes = receitas.groupby(['Centro de Custo','Month']).sum()[['Receita']].reset_index(drop=False)
    receita_mes = receitas.groupby('Month').sum()[['Receita']].reset_index(drop=False)

    carteiras_produto_mes = carteiras.groupby(['Produto', 'Month']).sum()[['NET']].reset_index(drop=False)
    carteiras_mes = carteiras.groupby('Month').sum()[['NET']].reset_index(drop=False)

    carteiras_produto_mes.rename(columns={'Produto':'Centro de Custo'}, inplace=True)

    media_mes = receita_mes.merge(carteiras_mes, how='left', on='Month')
    media_produto_mes = receita_produto_mes.merge(carteiras_produto_mes, how='left', on=['Centro de Custo','Month'])

    media_mes['ROA Fatorial'] = media_mes['Receita']/media_mes['NET']*12

    # captacao

    cod_filtrados = assessores.loc[assessores['Nome assessor'].isin(nomes_filtrados), 'Código assessor'].to_list()

    if not nomes_filtrados == ['Fatorial']:
        receitas = receitas[ receitas['Nome assessor'].isin(nomes_filtrados) ]
        captacao = captacao[ captacao['Nome assessor'].isin(nomes_filtrados) ]
        carteiras = carteiras[ carteiras['Assessor Relacionamento'].isin(cod_filtrados)]

    carteira = captacao.groupby('Month').sum()[['Net Em M']]
    carteira.columns = ['Carteira']
    resumo_receita = receitas.groupby('Month').sum()[['Receita']]
    resumo_receita = resumo_receita.merge(carteira, how='left', left_index=True, right_index=True)
    resumo_receita['ROA'] = resumo_receita['Receita'] / resumo_receita['Carteira'] * 12
    resumo_receita = resumo_receita.merge(media_mes[['Month', 'ROA Fatorial']], how='left',right_on='Month', left_index=True)
    resumo_receita.set_index('Month', inplace=True)
    
    export_files_rec = resumo_receita.copy()
    display_receitas = resumo_receita.copy()
    
    display_receitas['ROA'] *= 100
    display_receitas['ROA Fatorial'] *= 100

    col1, col2, col3, col4, col5 = st.columns(5)
    
    acumulado_2023 = resumo_receita.loc[['2023' in idx for idx in resumo_receita.index], 'Receita'].sum()

    meta = metas.loc[metas['Nome assessor'].isin(nomes_filtrados), 'Meta23'].sum()
    
    if nomes_filtrados == ['Fatorial']:
        meta = 13830000

    ultimo_mes_fechado = int(resumo_receita.index[-1][-2::])
    ultimo_mes_fechado = month[ultimo_mes_fechado-1]

    col1.metric(f"Receita {ultimo_mes_fechado}", 'R$ {:,.2f}'.format(sum(resumo_receita['Receita'].tail(1))))
    col2.metric("Média Móvel Três meses", 'R$ {:,.2f}'.format(sum(resumo_receita['Receita'].tail(3))/3))
    col3.metric("Acumulado 2023", 'R$ {:,.2f}'.format(acumulado_2023))
    col4.metric("Meta Mensal 2023", 'R$ {:,.2f}'.format(meta/12))
    col5.metric("Meta Total 2023", 'R$ {:,.2f}'.format(meta))

    mean_assessor_array = [resumo_receita['ROA'].mean() for i in resumo_receita['ROA']]

    col1, col2 = st.columns([2.5,1])

    fig = make_subplots(specs=[[{"secondary_y": True}]], row_heights=[450])

    fig.add_trace(go.Bar(x=resumo_receita.index, y=resumo_receita['Receita'], name='Receita', yaxis='y', width = 0.5))

    fig.add_trace(go.Scatter(x=resumo_receita.index, y=resumo_receita['ROA'], name='ROA'), secondary_y=True)

    fig.add_trace(go.Scatter(x=resumo_receita.index, y=resumo_receita['ROA Fatorial'], name='ROA Fatorial'), secondary_y=True)

    fig.add_trace(go.Scatter(x=resumo_receita.index, y=mean_assessor_array, name='ROA Médio Assessor', mode='lines', line=dict(width=2, dash='dot')), secondary_y=True)
    
    fig.update_traces(selector=dict(name='Receita'), marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',)
                  #marker_line_width=1.5, opacity=.96)
    
    fig.update_traces(selector=dict(name='ROA'), marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',)
                  #marker_line_width=1.5, opacity=.96)
    
    fig.update_traces(selector=dict(name='ROA Fatorial'), marker_color='rgb(149, 149, 149)', marker_line_color='rgb(149, 149, 149)')
                  #marker_line_width=1.5, opacity=.96)

    fig.update_traces(selector=dict(name='ROA Médio Assessor'), marker_color='rgb(68, 81, 103)', marker_line_color='rgb(68, 81, 103)',
                  marker_line_width=1.5, opacity=.96)

    fig.update_yaxes(showgrid=False, rangemode='tozero', tickformat = ".2%", secondary_y=True)
    
    col1.plotly_chart(fig, use_container_width=True)

    col2.write(display_receitas.style.format({'Carteira':'R$ {:,.2f}', 'Receita':'R$ {:,.2f}', 'ROA':'{:,.3f} %', 'ROA Fatorial':'{:,.3f} %'}))

    df = to_excel(export_files_rec)

    col2.download_button(
        label='Exportar Receita',
        data = df,
        file_name = f'Receita 2022.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    st.write('''
    ### Distribuição da Receita
    ''')

    col1, col2 = st.columns(2)

    month = resumo_receita.index.to_list()
    
    start_month, end_month = col1.selectbox('Mês Inicial', month, 0), col2.selectbox('Mês Final', month, len(month)-1)
    
    start_idx = month.index(start_month)
    end_idx = month.index(end_month)

    n_month = abs(start_idx - end_idx) + 1

    receitas_filt = receitas[receitas['Month'].isin( month[start_idx : end_idx + 1 : ] )]
    
    media_produto_mes = media_produto_mes.loc[media_produto_mes['Month'].isin( month[start_idx : end_idx + 1 : ] )]
    media_produto_mes = media_produto_mes.groupby('Centro de Custo').sum()[['Receita','NET']].reset_index(drop=False) 
    #media_produto_mes[['Receita', 'NET']] /= len(month[start_idx : end_idx + 1 : ])
    media_produto_mes['ROA Fatorial'] = media_produto_mes['Receita'] / media_produto_mes['NET'] * 12
    media_produto_mes.sort_values('Receita', inplace=True, ascending=False)
    media_produto_mes.rename(columns={'Receita':'Receita Fatorial'}, inplace=True)

    receitas_filt = receitas_filt.groupby(['Centro de Custo']).sum().reset_index()

    receitas_filt['% Receita'] = receitas_filt['Receita']/sum(receitas_filt['Receita'])

    receitas_filt= receitas_filt.merge(media_produto_mes[['Centro de Custo', 'Receita Fatorial']],how='left',on='Centro de Custo')

    receitas_filt['% Receita Fatorial'] = receitas_filt['Receita Fatorial']/sum(receitas_filt['Receita Fatorial'])

    carteiras_filt = carteiras[carteiras['Month'].isin( month[start_idx : end_idx + 1 : ] )]

    carteiras_filt = carteiras_filt.groupby('Produto').sum()[['NET']].reset_index(drop=False)
    carteiras_filt['NET'] /= n_month

    carteiras_filt.columns = ['Produto','PL Médio Mês']

    receitas_filt = receitas_filt.merge(carteiras_filt, how='left', left_on='Centro de Custo', right_on='Produto')
    del receitas_filt['Produto']

    receitas_filt['ROA'] = receitas_filt['Receita'] / receitas_filt['PL Médio Mês'] * 12/n_month

    del receitas_filt['PL Médio Mês']

    receitas_filt = receitas_filt.merge(media_produto_mes[['Centro de Custo', 'ROA Fatorial']], how='left', on='Centro de Custo')
    receitas_filt = receitas_filt.fillna(0).sort_values('Receita', ascending=False)

    fig = px.pie(receitas_filt, 'Centro de Custo', 'Receita')

    fig.update_traces(marker_colors=[f'rgb({29 + 30*i},{40 + 30*i},{67 + 30*i})' for i in range(len(receitas_filt.index))])
    
    fig.update_layout(title=f'<b>Disposição da Receita {nomes_filtrados[0]}</b>', barmode='stack',
                         title_x=0.5, title_font_size=20)

    col1, col2 = st.columns(2)

    col1.plotly_chart(fig, use_container_width=True)

    display_df = receitas_filt.copy().set_index('Centro de Custo')
    display_df['ROA'] *= 100
    display_df['ROA Fatorial'] *= 100
    display_df['% Receita'] *= 100
    display_df['% Receita Fatorial'] *= 100

    del display_df['Ano']
    
    col2.write(display_df.style.format({
        'Receita Fatorial':'R$ {:,.2f}', 
        'ROA Fatorial':'{:,.3f} %', 
        'Receita':'R$ {:,.2f}', 
        'ROA':'{:,.3f} %',
        '% Receita':'{:,.2f} %',
        '% Receita Fatorial':'{:,.2f} %'}))

    df = to_excel(receitas_filt)

    col2.download_button(
        label='Receita por Área',
        data = df,
        file_name = f'Receita por Área {start_month}-{end_month}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )



