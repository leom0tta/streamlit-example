from imports import st, pd

from functions import to_excel, Get
from config import adms, private, exclusive, digital, team_jansen

def app(name):

    aniversario = Get.aniversario()

    aniversario.replace('Atendimento', 'Atendimento Fatorial', inplace=True)
    
    st.write('''
    # Aniversário de Clientes
    ''')

    if name in adms:
        nomes_filtrados = st.multiselect('Assessor', ['Fatorial'] + aniversario['Nome assessor Relacionamento'].drop_duplicates().fillna(aniversario['Assessor']).sort_values().to_list(), 'Fatorial')

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

    if nomes_filtrados != ['Fatorial']:
        aniversario = aniversario[aniversario['Nome assessor Relacionamento'].isin(nomes_filtrados) | aniversario['Nome assessor Indicador'].isin(nomes_filtrados)]

    col1, col2 = st.columns([1,2])

    aniversario['Data de Aniversário'] = pd.to_datetime(aniversario['Data de Aniversário'])

    bottom = pd.to_datetime(col1.date_input('Aniversário partir de:'))
    top = pd.to_datetime(col1.date_input('Aniversário até:'))
    mask_date_input = (aniversario['Data de Aniversário'] >= bottom) & (aniversario['Data de Aniversário'] <= top)

    aniversario['Data de Aniversário'] = aniversario['Data de Aniversário'].dt.strftime('%m/%d/%Y')

    filt_aniversario = aniversario[mask_date_input]

    display_df = filt_aniversario[['Nome assessor Relacionamento', 'Cliente', 'NomeCliente', 'Nome assessor Indicador', 'Data de Aniversário']]

    col2.write(display_df)

    df = to_excel(aniversario, index=False)

    col1.download_button('Tabela Completa de Aniversariantes', df, f'Aniversario_Clientes_{nomes_filtrados}.xlsx')