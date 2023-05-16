from imports import st, pd, timedelta, date

from functions import to_excel, Get, Dataframe
from config import adms, private, exclusive, digital, team_jansen
from config import assessores, clientes_rodrigo, suitability, diversificador, saldos
from config import most_recent_data

def app(name, diversificador=diversificador, saldos=saldos, suitability = suitability, clientes_rodrigo=clientes_rodrigo, assessores=assessores, most_recent_data=most_recent_data):

    diversificador = diversificador.loc[~diversificador['Data de Vencimento'].isna()]
    diversificador = diversificador.loc[diversificador['Produto'] == 'Renda Fixa']
    diversificador['Data de Vencimento'] = pd.to_datetime(diversificador['Data de Vencimento'])
    
    st.write('''
    # Vencimentos Renda Fixa
    ''')

    if name in adms + ['Rafael Abdalla']: # líder de RF
        nomes_filtrados = st.multiselect('Assessor', ['Fatorial'] + assessores['Nome assessor'].sort_values().to_list(), 'Fatorial')

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
    
    diversificador_obj = Dataframe(diversificador)
    diversificador_obj.add_assessor_relacionamento(clientes_rodrigo)
    diversificador_obj.add_nome_cliente(suitability)
    diversificador_obj.add_nome_assessor(assessores)
    diversificador = diversificador_obj.dataframe

    saldos_obj = Dataframe(saldos)
    saldos_obj.add_nome_assessor(assessores)
    saldos = saldos_obj.dataframe

    diversificador['Nome assessor'].fillna(diversificador['Assessor'])

    if nomes_filtrados != ['Fatorial']:
        
        diversificador = diversificador[diversificador['Nome assessor'].isin(nomes_filtrados)]
        saldos = saldos[ saldos['Nome assessor'].isin(nomes_filtrados) ]

    saldos_acima_10k = saldos.loc[saldos['D0'] >= 1e5]
    saldos_acima_10k = saldos_acima_10k[['Cliente', 'NomeCliente', 'Nome assessor', 'D0']]
    saldos_acima_10k.rename(columns={'D0':'Saldos D0'}, inplace=True)
    saldos_acima_10k.sort_values('Saldos D0', ascending=False, inplace=True)
    
    seven_days_from_now = pd.to_datetime(date.today() + timedelta(7))

    vencimentos_essa_semana = diversificador.loc[diversificador['Data de Vencimento'] < seven_days_from_now , :]

    n_clientes_vencendo = len(vencimentos_essa_semana['Cliente'].drop_duplicates())
    sum_vencimentos = 'R$ {:,.2f}'.format(sum(vencimentos_essa_semana['NET']))
    n_cientes_saldo_acima = len(saldos_acima_10k['Cliente'].drop_duplicates())
    vol_saldo_acima = 'R$ {:,.2f}'.format(sum(saldos['D0']))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric('Clientes com Saldo Acima de 10.000', f'{n_cientes_saldo_acima} clientes')
    col2.metric('Volume do Saldo em D0', f'{vol_saldo_acima}')
    col3.metric('Quantidade de Vencimentos | 7 dias', f'{n_clientes_vencendo} clientes')
    col4.metric('Volume de Vencimentos | 7 dias', f'{sum_vencimentos}')

    col1, col2 = st.columns(2)

    bottom = pd.to_datetime(col1.date_input('Vencem a partir de:'))
    top = pd.to_datetime(col2.date_input('Vencem até:', pd.to_datetime(date.today() + timedelta(7)), ))

    col1, space,  col2 = st.columns([1.25,.05, 1.7])
    
    mask_date_input =( diversificador['Data de Vencimento'] >= bottom) & (diversificador['Data de Vencimento'] <= top)

    filt_vencimento = diversificador[mask_date_input]

    if nomes_filtrados == ['Fatorial']:

        display_df = filt_vencimento[['Nome assessor', 'Cliente', 'NomeCliente', 'Ativo', 'Data de Vencimento', 'NET']]

    else:
        display_df = filt_vencimento[['Cliente', 'NomeCliente', 'Ativo', 'Data de Vencimento', 'NET']]
        del saldos_acima_10k['Nome assessor']

    display_df['Data de Vencimento'] = display_df['Data de Vencimento'].dt.strftime('%m/%d/%Y')

    display_df = display_df.style.format({'Quantidade':'{:,.2f}', 'NET':'R$ {:,.2f}'})
    display_df.hide_index()

    saldos_acima_10k = saldos_acima_10k.style.format({'Saldos D0':'R$ {:,.2f}'})
    saldos_acima_10k.hide_index()

    col2.write(display_df, index_col=False)

    col1.write(saldos_acima_10k, index_col=False)

    df = to_excel(saldos, index=False)

    col1.download_button('Tabela Completa Saldos', df, f'Saldos_{nomes_filtrados}.xlsx')

    df = to_excel(filt_vencimento, index=False)

    col2.download_button('Tabela Completa de Vencimentos', df, f'Vencimentos_RF_{nomes_filtrados}.xlsx')