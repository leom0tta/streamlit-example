from imports import st, pd, px, go, datetime, make_subplots

from functions import Data, Get, Dataframe, LandingPage, ApiError
from functions import to_excel, horizontal_singular_bar, espacamento, get_meses, get_most_recent_data
from config import contas_novas, most_recent_data, clientes_rodrigo, suitability, adms, assessores , private, exclusive, digital, team_jansen, landing_page_relatorios

pd.options.plotting.backend = "plotly"

def app(name, most_recent_data=most_recent_data, contas_novas=contas_novas, assessores=assessores):

    st.write("""
    # Fatorial Site
    """)

    # header

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

        most_recent_data = Data(most_recent_data).datetime

        header1, header2 = st.columns(2)
    
        data_hoje = get_most_recent_data(header1.date_input('Data do Relatório', most_recent_data))
        mes = Data(data_hoje).text_month

        relatorio = header2.selectbox('Selecione o Relatório: ', landing_page_relatorios)

        posi = Get.captacao(data_hoje, sheet_name='Positivador M')
            
        novos_transf = Get.captacao(data_hoje, sheet_name='Novos + Transf')
        perdidos = Get.captacao(data_hoje, sheet_name='Perdidos')
        
        if relatorio == 'Receita':

            tags = Get.tags()
            categorias = Get.receitas_cliente()[['Cliente', 'NomeCliente', 'Category']].drop_duplicates()

            mes, ano = Data(data_hoje).month , Data(data_hoje).year

            while True:
                try:
                    if mes > 10: 
                        cod = f'01{mes}{ano}'
                    else: 
                        cod =f'010{mes}{ano}'
                    
                    receita = Get.receitas(cod)
                    st.write(f'Não há dados para o mês selecionado, mostrando receitas em {Data(cod).text_month}.')
                    
                    break
                except ApiError:
                    if mes == 1:
                        mes = 12
                        ano -= 1
                    else:
                        mes -= 1

        positivador = posi.copy()

        cod_filtrados = assessores.loc[assessores['Nome assessor'].isin(nomes_filtrados), 'Código assessor'].to_list()

        if not nomes_filtrados == ['Fatorial']:

            posi = posi.loc[posi['Assessor correto'].isin(cod_filtrados)]
            novos_transf = novos_transf.loc[novos_transf['Assessor'].isin(cod_filtrados)]
            perdidos = perdidos.loc[perdidos['Assessor correto'].isin(cod_filtrados)]
            contas_novas = contas_novas.loc[contas_novas['Assessor Indicador'].astype(str).isin(cod_filtrados)]

    if relatorio == 'Carteira':

        col1, col2 = st.columns([1,3]) 

        number_of_clients = len(posi.index)

        espacamento(3, col1)
        col1.metric('Total de Clientes', f'{number_of_clients} clientes')

        ativos = len(posi[posi['Status'] == 'ATIVO'].index)
        inativos = len(posi[posi['Status'] == 'INATIVO'].index)

        data = {'Clientes Ativos': [ativos], 'Clientes Inativos':[inativos]}
        title = 'Separação Clientes Ativos e Inativos'

        horizontal_singular_bar(data, reference=col2)

        col1, col2 = st.columns(2)

        month = get_meses()

        dict_month = pd.DataFrame( [[ month[i] , j, datetime.datetime(2000 + j, i+1, 1).strftime("%Y - %m")] for i in range(12) for j in [22,23,24]] , columns = ['Mes', 'Ano', 'Month'])

        contas_novas = contas_novas.merge(dict_month, how='left', on=['Ano', 'Mes'])

        contas_novas.sort_values('Month', inplace=True, ascending=False)

        periodos = contas_novas['Month'].drop_duplicates().head(6)

        contas_novas = contas_novas.loc[contas_novas['Month'].isin(periodos)]

        fig = go.Figure()

        resumo_contas_maiores_300k = contas_novas.loc[contas_novas['Net Em M'] >= 3e5].groupby('Month').count()[['Cliente']].reset_index(drop=False)
        resumo_contas_menores_300k = contas_novas.loc[contas_novas['Net Em M'] < 3e5].groupby('Month').count()[['Cliente']].reset_index(drop=False)

        fig.add_trace(go.Bar(x = resumo_contas_menores_300k['Month'], y=resumo_contas_menores_300k['Cliente'], 
                             name='-300k', width=.5, 
                             marker_color='rgb(29,40,67)',
                             ))
        fig.add_trace(go.Bar(x = resumo_contas_maiores_300k['Month'], y=resumo_contas_maiores_300k['Cliente'], 
                             name='+300k', width=.5, 
                             marker_color='rgb(125, 147, 189)',
                             ))
        
        fig.update_layout(title='<b>Contas novas do último semestre</b>', barmode='stack',
                          title_x=0.5, title_font_size=20)

        col1.plotly_chart(fig, use_container_width=True)

        perdidos_display = LandingPage.get_perdidos_display(perdidos, suitability)
        

        mask_faixa_2 = posi['Net Em M'] > 100000
        mask_faixa_3 = posi['Net Em M'] > 300000
        mask_faixa_4 = posi['Net Em M'] > 500000
        mask_faixa_5 = posi['Net Em M'] > 1000000
        mask_faixa_6 = posi['Net Em M'] > 3000000

        posi['Faixa'] = 'i. >100k'

        posi.loc[mask_faixa_2, 'Faixa'] = 'ii. 100k-300k'
        posi.loc[mask_faixa_3, 'Faixa'] = 'iii. 300k-500k'
        posi.loc[mask_faixa_4, 'Faixa'] = 'iv. 500k-1MM'
        posi.loc[mask_faixa_5, 'Faixa'] = 'v. 1MM-3MM'
        posi.loc[mask_faixa_6, 'Faixa'] = 'vi. +3MM'

        faixas = posi.groupby('Faixa').count()[['Cliente']].reset_index(drop=False)
        title = '<b>Disposição de Clientes por Patrimônio</b>'

        fig = px.funnel(faixas, x='Cliente', y='Faixa', title=title)

        fig.update_traces(marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)
        
        fig.update_layout(title_x=0.5, title_font_size=20)

        col2.plotly_chart(fig, use_container_width=True)

        novos_transf_display = LandingPage.get_novos_transf_display(novos_transf, suitability)
        
        col1.write(f'##### Clientes Novos em {mes}')
        col1.dataframe(novos_transf_display)

        col2.write(f'##### Clientes Perdidos em {mes}')
        col2.dataframe(perdidos_display)

        

    elif relatorio == 'Captação':

        col1, col2 = st.columns([1,3])
        
        captacao_externa = posi.loc[~posi['Cliente'].isin(novos_transf['Cliente']), 'Captação Líquida em M'].sum()
        captacao_interna = novos_transf['Net em M-1'].sum() + novos_transf['Captação Líquida em M'].sum() - perdidos['Net Em M'].sum()

        captacao = captacao_externa + captacao_interna

        espacamento(3, col1)
        col1.metric('Captação Líquida', 'R$ {:,.2f}'.format(captacao))

        data = {'Captação Interna': [captacao_interna], 'Captação Externa':[captacao_externa]}
        title = 'Separação de Captação entre Externa e Interna'

        horizontal_singular_bar(data, reference=col2)

        # maiores captacoes

        df_capt_ext = posi[['Cliente', 'Captação Líquida em M']].sort_values('Captação Líquida em M', ascending=False)#.head(10)
        df_capt_ext = df_capt_ext.loc[ df_capt_ext['Captação Líquida em M'] > 0]
        df_capt_ext.columns = ['Cliente', 'Captação']
        df_capt_ext['Natureza'] = 'Externa'

        df_capt_int = novos_transf[['Cliente', 'Captação Líquida em M', 'Net em M-1']]
        df_capt_int['Captação'] = df_capt_int['Net em M-1'] + df_capt_int['Captação Líquida em M']
        df_capt_int = df_capt_int[['Cliente', 'Captação']]
        df_capt_int['Natureza'] = 'Interna'

        df_capt_ext = df_capt_ext.loc[~df_capt_ext['Cliente'].isin(df_capt_int['Cliente'])]

        df_capt_int = df_capt_int.sort_values('Captação', ascending=False)#.head(10)

        df_capt = pd.concat([df_capt_ext, df_capt_int], axis=0).sort_values('Captação', ascending = False)#.head(10)

        df_retirada_ext = posi[['Cliente', 'Captação Líquida em M']].sort_values('Captação Líquida em M', ascending=False)#.tail(10)
        df_retirada_ext = df_retirada_ext.loc[ df_retirada_ext['Captação Líquida em M'] < 0]
        df_retirada_ext.columns = ['Cliente', 'Captação']
        df_retirada_ext['Natureza'] = 'Externa'

        df_retirada_int = perdidos[['Cliente', 'Net Em M']]
        df_retirada_int['Captação'] = -1*df_retirada_int['Net Em M']
        df_retirada_int = df_retirada_int[['Cliente', 'Captação']]
        df_retirada_int['Natureza'] = 'Interna'

        df_retirada_int = df_retirada_int.sort_values('Captação', ascending=False)#.tail(10)
        
        df_retirada = pd.concat([df_retirada_ext, df_retirada_int], axis=0).sort_values('Captação', ascending = True)#.head(10)
        
        obj_df_capt = Dataframe(df_capt)
        obj_df_retirada = Dataframe(df_retirada)
        
        obj_df_capt.add_nome_cliente(suitability)
        obj_df_capt.reorder_columns('NomeCliente', 1)

        obj_df_retirada.add_nome_cliente(suitability)
        obj_df_retirada.reorder_columns('NomeCliente', 1)

        if nomes_filtrados == ['Fatorial']:
            
            obj_df_capt.dataframe = obj_df_capt.dataframe.merge(positivador[['Cliente', 'Net em M-1', 'Assessor correto']], how='left', on='Cliente')
            obj_df_capt.add_nome_assessor(assessores, column_assessor='Assessor correto')
            obj_df_capt.dataframe.rename(columns={'Nome assessor':'Assessor'}, inplace=True)
            df_capt = obj_df_capt.dataframe
            df_capt = df_capt[['Assessor', 'Cliente', 'NomeCliente', 'Captação', 'Net em M-1', 'Natureza']]

            obj_df_retirada.dataframe = obj_df_retirada.dataframe.merge(positivador[['Cliente', 'Net em M-1', 'Assessor correto']], how='left', on='Cliente')
            obj_df_retirada.add_nome_assessor(assessores, column_assessor='Assessor correto')
            obj_df_retirada.dataframe.rename(columns={'Nome assessor':'Assessor'}, inplace=True)
            df_retirada = obj_df_retirada.dataframe
            df_retirada = df_retirada[['Assessor', 'Cliente', 'NomeCliente', 'Captação', 'Net em M-1', 'Natureza']]

        else:
            
            df_capt = obj_df_capt.dataframe
            df_capt = df_capt.merge(positivador[['Cliente', 'Net em M-1']])
            df_capt = df_capt[['Cliente', 'NomeCliente', 'Captação', 'Net em M-1', 'Natureza']]

            df_retirada = obj_df_retirada.dataframe
            df_retirada = df_retirada.merge(positivador[['Cliente', 'Net em M-1']])
            df_retirada['Net em M-1'].fillna(df_retirada['Captação'], inplace=True)
            df_retirada = df_retirada[['Cliente', 'NomeCliente', 'Captação', 'Net em M-1', 'Natureza']]

        plot_retiradas = df_retirada.copy()
        plot_captacao = df_capt.copy()

        #df_capt['Captação'] = df_capt['Captação'].apply(lambda x: 'R$ {:,.2f}'.format(x))
        #df_retirada['Captação'] = df_retirada['Captação'].apply(lambda x: 'R$ {:,.2f}'.format(x))

        st.markdown("<h3 style='text-align: center;'>10 clientes com maiores captações </h3>", unsafe_allow_html=True)

        col1,col2 = st.columns([1.4,1])

        espacamento(1,col1)

        df_capt = df_capt.rename(columns={'Net em M-1':'PL Mês Passado'})
        df_capt[r'% PL'] = abs(df_capt['Captação']/df_capt['PL Mês Passado'])*100

        if nomes_filtrados == 'Fatorial':
        
            df_capt = df_capt[['Cliente','Assessor', 'NomeCliente', 'Captação', '% PL', 'PL Mês Passado', 'Natureza']]

        else:
            df_capt = df_capt[['Cliente', 'NomeCliente', 'Captação', '% PL', 'PL Mês Passado', 'Natureza']]
        
        col1.write(df_capt.set_index('Cliente').style.format({'Captação':'R$ {:,.2f}','PL Mês Passado':'R$ {:,.2f}',r'% PL':'{:,.3f} %'}))
        
        df = to_excel(df_capt)

        col1.download_button(
            label='Exportar Captação',
            data = df,
            file_name = f'Captação por Clientes.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_captacao['Cliente'].head(10), y=plot_captacao['Captação'].head(10), width=.5))
        fig.update_traces(marker_color='rgb(125, 147, 189)', marker_line_color='rgb(125, 147, 189)',
                  marker_line_width=1.5, opacity=.96)

        col2.plotly_chart(fig, use_container_width=True)

        st.markdown("<h3 style='text-align: center;'>10 clientes com maiores retiradas </h3>", unsafe_allow_html=True)

        col1,col2 = st.columns([1.4,1])

        espacamento(1,col1)

        df_retirada = df_retirada.rename(columns={'Net em M-1':'PL Mês Passado'})
        df_retirada[r'% PL'] = abs(df_retirada['Captação']/df_retirada['PL Mês Passado'])*100
        
        if nomes_filtrados == ['Fatorial']:
            df_retirada = df_retirada[['Cliente','Assessor', 'NomeCliente', 'Captação', '% PL', 'PL Mês Passado', 'Natureza']]
        else:
            df_retirada = df_retirada[['Cliente', 'NomeCliente', 'Captação', '% PL', 'PL Mês Passado', 'Natureza']]
        df_retirada.drop_duplicates(subset=['Cliente'], inplace=True)

        col1.write(df_retirada.set_index('Cliente').style.format({'Captação':'R$ {:,.2f}','PL Mês Passado':'R$ {:,.2f}',r'% PL':'{:,.3f} %'}))
        df = to_excel(df_retirada)

        col1.download_button(
            label='Exportar Captação',
            data = df,
            file_name = f'Captação por Clientes.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_retiradas['Cliente'].head(10), y=plot_retiradas['Captação'].head(10), width=.5))

        fig.update_traces(marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)

        col2.plotly_chart(fig, use_container_width=True)

    elif relatorio == 'Receita':

        receita = LandingPage.filter_receita(receita, assessores, clientes_rodrigo)

        if nomes_filtrados != ['Fatorial']:
            receita = receita.loc[receita['Nome assessor'].isin(nomes_filtrados)]

        mask_atende_e_indica = receita['Assessor Dono'] == receita['Assessor Indicador']

        receita_cliente_proprio = receita.loc[mask_atende_e_indica, 'Valor Bruto Recebido'].sum()
        receita_cliente_emprestado = receita.loc[~mask_atende_e_indica, 'Valor Bruto Recebido'].sum()

        col1, col2 = st.columns([1.4,1])

        espacamento(3, col1)
        col1.metric('Receita Total', 'R$ {:,.2f}'.format(receita['Valor Bruto Recebido'].sum()))

        data = {'Receita de Clientes Próprios': [receita_cliente_proprio], 'Receita de Clientes de Outras Pessoas':[receita_cliente_emprestado]}

        horizontal_singular_bar(data, reference=col2)

        df_cliente, df_tags = LandingPage.get_receitas_tag_clientes(receita, tags, categorias, positivador)

        col1, col2 = st.columns(2)

        fig = px.pie(df_tags.reset_index(drop=False), 'Centro de Custo', 'Valor Bruto Recebido', title='Segmentação da Receita por Centro de Custo')

        fig.update_traces(marker_colors=[f'rgb({29 + 30*i},{40 + 30*i},{67 + 30*i})' for i in range(len(df_tags.index))],
        marker_line_width=.5, opacity=.96)

        fig.update_layout(title_x=0.5, title_font_size=20)

        col1.plotly_chart(fig, use_container_width=True)

        title = 'Segmentação da Receita Por Tipo de Cliente'

        df_display = df_cliente.groupby(['Faixa', 'Category']).sum()[['Valor Bruto Recebido']].reset_index(drop=False)

        fig = px.bar(df_display, x='Valor Bruto Recebido', y='Faixa', color='Category', title=title, color_discrete_sequence=['#1D2843','#6e7a9b' ,'#bdc0c8'])
        
        fig.update_layout(title_x=0.5, title_font_size=20)

        col2.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns([1,.5,.5])

        display_df_cliente = df_cliente.sort_values(ascending=False, by='Valor Bruto Recebido').head(10)

        display_df_tags = df_tags.copy()

        display_df_faixa_pl = df_cliente.groupby('Faixa').sum()[['Valor Bruto Recebido']].sort_values('Valor Bruto Recebido', ascending=False)
        
        col1.write("##### 10 clientes com maior receita no mês")
        col1.write(display_df_cliente[['Cliente', 'NomeCliente', 'Faixa', 'Category', 'Valor Bruto Recebido']].style.format({'Valor Bruto Recebido':'R$ {:,.2f}'}))
        
        col2.write("##### Distribuição da Receita por Vertical")
        col2.write(display_df_tags.style.format({'Valor Bruto Recebido':'R$ {:,.2f}'}))

        col3.write("##### Distribuição da Receita por Faixa de PL")
        col3.write( display_df_faixa_pl.style.format({'Valor Bruto Recebido':'R$ {:,.2f}'}) )
        

        





        
    


