from imports import st

import text_data
from functions import get_most_recent_data, espacamento, get_cod_data, to_excel, get_filtered_posi, get_filtered_diversificador, display_relatorio_info, get_captacao_por_cliente, filter_receita, filter_captacao, filter_nps, Get, Data
from config import receitas, captacao, most_recent_data, list_relatorios, list_relatorios_adm, assessores, adms, team_jansen, private, exclusive, digital


def app(name, most_recent_data=most_recent_data):
    
    st.write('''
    # Relatórios
    ''')

    col1, col2 = st.columns(2)

    if name in adms:
        nomes_filtrados = col1.multiselect('Assessor', ['Fatorial'] + assessores['Nome assessor'].drop_duplicates().sort_values().to_list(), 'Fatorial')

    elif name in team_jansen:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Jansen Costa', 'Private'], name)
    
    elif name in private:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Private'], name)
    
    elif name in exclusive:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Exclusive', 'Atendimento Fatorial'], name)

    elif name in digital:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Atendimento Fatorial'], name)

    else:
        nomes_filtrados = [name]
    
    espacamento(1, st)

    if name in adms:
        relatorio = col2.multiselect('Selecione o relatório:', list_relatorios + list_relatorios_adm)
    
    else:
        relatorio = col2.multiselect('Selecione o relatorio: ', list_relatorios)

    espacamento(1, st)

    if relatorio == ['Relatórios XP']:

        # positivador

        disparar_posi, selected_data = display_relatorio_info(
            title='Positivador', 
            data_hoje=most_recent_data, 
            explanation= text_data.positivador_explanation
        )

        if disparar_posi:

            data_hoje = get_most_recent_data(input_date=selected_data)
            
            posi = get_filtered_posi(nomes_filtrados, data_hoje, assessores)
            
            df = to_excel(posi, index=False)
            
            st.download_button(
                label='Baixar o positivador',
                data=df,
                file_name = f'positivador_{nomes_filtrados[0]}_{data_hoje}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

        # diversificador

        disparar_div, selected_data = display_relatorio_info(
            title='Diversificador', 
            data_hoje=most_recent_data, 
            explanation= text_data.diversificador_explanation
            )

        if disparar_div:

            data_hoje = get_most_recent_data(input_date=selected_data)
            
            if nomes_filtrados == ['Fatorial']:
                diversificador = Get.diversificador(data_hoje)
            else: 
                diversificador = get_filtered_diversificador(nomes_filtrados, data_hoje, assessores)
            
            df = to_excel(diversificador, index=False)
            
            st.download_button(
                label='Baixar diversificador',
                data=df,
                file_name = f'diversificacao_{nomes_filtrados[0]}_{data_hoje}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    
    if relatorio == ['Relatórios Inteligência']:

        disparar_capt, selected_data = display_relatorio_info(
            title='Captação por Cliente', 
            data_hoje=most_recent_data, 
            explanation= text_data.captacao_explanation
            )

        if disparar_capt:
            
            data_hoje = get_most_recent_data(input_date=selected_data)

            capt = get_captacao_por_cliente(data_hoje, nomes_filtrados, assessores)

            df = to_excel(capt, index=False)
            
            st.download_button(
                label='Baixar Captação por Cliente',
                data=df,
                file_name = f'captacao_datalhada_{nomes_filtrados[0]}_{data_hoje}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    
    if relatorio == ['Performance Geral']:
        
        disparar_roa, selected_data = display_relatorio_info(
            title='ROA da Empresa', 
            data_hoje=most_recent_data, 
            explanation= text_data.roa_explanation
            )
        
        if disparar_roa:
            
            roa_total = Get.roa_total()

            mes = Data(get_cod_data(selected_data)).text_month

            roa_mensal = roa_total[roa_total['Mes'] == mes]

            roa_mensal.rename(columns={'ROA Relacionamento': f'ROA {mes}'}, inplace=True)

            roa_anual = roa_total.groupby('Nome assessor').sum()[['Receita Relacionamento', 'Patrimônio Relacionamento']].reset_index()

            roa_anual['ROA Anual'] = roa_anual['Receita Relacionamento']/roa_anual['Patrimônio Relacionamento'] * 12

            df = roa_mensal[['Nome assessor', f'ROA {mes}']].merge(roa_anual[['Nome assessor', 'ROA Anual']], how='outer', on='Nome assessor')

            df = to_excel(df, index=False)
            
            st.download_button(
                label='Baixar ROA Relacionamento',
                data=df,
                file_name = f'captacao_detalhada_{nomes_filtrados[0]}_{mes}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        disparar_receitas, selected_data = display_relatorio_info(
            title='Receitas 2022', 
            data_hoje=most_recent_data, 
            explanation= text_data.receitas_2022_explanation,
            input_list=['Apenas assessores', 'Apenas Verticais', 'Assessores por Vertical', 'Assessores por mês', 'Verticais por mês', 'Assessores por vertical por mês']
            )    

        if disparar_receitas:
            df = filter_receita(selected_data, receitas)

            df = to_excel(df, index=False, sheet_names = selected_data)

            st.download_button(
                label=f'Baixar Receita',
                data=df,
                file_name = f'receita_2022_{selected_data}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        disparar_captacao, selected_data = display_relatorio_info(
            title='Captacao 2022', 
            data_hoje=most_recent_data, 
            explanation= text_data.captacao_explanation,
            input_list=['Apenas assessores', 'Assessores por mês']
            )    

        if disparar_captacao:
            df = filter_captacao(selected_data, captacao)

            df = to_excel(df, index=False)

            st.download_button(
                label=f'Baixar Captacao',
                data=df,
                file_name = f'captacao_2022_{selected_data}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        disparar_nps, selected_data = display_relatorio_info(
            title='NPS 2022', 
            data_hoje=most_recent_data, 
            explanation= text_data.NPS_2022_explanation,
            input_list = ['2022']
            )

        if disparar_nps:
            df = filter_nps(selected_data[0], assessores)

            df = to_excel(df, index=False)

            st.download_button(
                label=f'Baixar NPS Anual',
                data=df,
                file_name = f'NPS_{selected_data}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        
        



