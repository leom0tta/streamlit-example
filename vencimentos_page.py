from imports import st, pd, timedelta, date

from functions import to_excel, Get, Dataframe
from config import adms, private, exclusive, digital, team_jansen
from config import assessores, clientes_rodrigo, suitability
from config import most_recent_data

def app(name, suitability = suitability, clientes_rodrigo=clientes_rodrigo, assessores=assessores, most_recent_data=most_recent_data):

    diversificador = Get.diversificador(most_recent_data)
    diversificador = diversificador.loc[~diversificador['Data de Vencimento'].isna()]
    diversificador = diversificador.loc[diversificador['Produto'] == 'Renda Fixa']
    diversificador['Data de Vencimento'] = pd.to_datetime(diversificador['Data de Vencimento'], format = "%dd/%mm/%yy")
    print(diversificador['Data de Vencimento'])
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

    diversificador['Nome assessor'].fillna(diversificador['Assessor'])

    if nomes_filtrados != ['Fatorial']:
        
        diversificador = diversificador[diversificador['Nome assessor'].isin(nomes_filtrados)]

    seven_days_from_now = pd.to_datetime(date.today() + timedelta(7))

    vencimentos_essa_semana = diversificador.loc[diversificador['Data de Vencimento'] < seven_days_from_now, 'Ativo'].drop_duplicates()

    col1, col2 = st.columns([1,2])

    bottom = pd.to_datetime(col1.date_input('Vencem a partir de:'))
    top = pd.to_datetime(col1.date_input('Vencem até:'))
    mask_date_input =( diversificador['Data de Vencimento'] >= bottom) & (diversificador['Data de Vencimento'] <= top)

    filt_vencimento = diversificador[mask_date_input]

    display_df = filt_vencimento[['Nome assessor', 'Cliente', 'NomeCliente', 'Ativo', 'Data de Vencimento', 'Quantidade', 'NET']]

    display_df['Data de Vencimento'] = display_df['Data de Vencimento'].dt.strftime('%m/%d/%Y')

    col2.write(display_df.style.format({'Quantidade':'{:,.2f}', 'NET':'R$ {:,.2f}'}))

    df = to_excel(filt_vencimento, index=False)

    col1.download_button('Tabela Completa de Vencimentos', df, f'Aniversario_Clientes_{nomes_filtrados}.xlsx')