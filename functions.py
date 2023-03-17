from imports import inf, date, timedelta, st, np, pd , datetime
from imports import MIMEApplication, MIMEMultipart, MIMEText, smtplib
from imports import px, sleep
from imports import ApiError, closing, io, dropbox 

dbx = dropbox.Dropbox(
        app_key=st.secrets['appKey'],
        app_secret=st.secrets['appSecret'],
        oauth2_refresh_token=st.secrets['refreshToken']
)

class Dataframe:
    def __init__(self, my_dataframe):
        self.dataframe = my_dataframe

    def rows(self):
        return len(self.dataframe.index)

    def cols(self):
        return len(self.dataframe.columns)


    def add_assessor_indicador(self, clientes_rodrigo, column_conta='Cliente', column_assessor='Assessor', assessores_com_A = False, positivador=None, inplace=True, com_obs=False):
        """Essa função  adiciona a coluna de assessor relacionamento a um dataframe com coluna de contas"""
        dataframe = self.dataframe
        if assessores_com_A == False:
            clientes_rodrigo['Assessor Indicador'] = clientes_rodrigo['Assessor Indicador'].str.strip('A')
            clientes_rodrigo['Assessor Indicador'] = clientes_rodrigo['Assessor Indicador'].str.replace('tendimento Fatorial', 'Atendimento Fatorial')
        if com_obs:
            clientes_rodrigo = clientes_rodrigo[['Conta' , 'Assessor Indicador', 'OBS']]
        else:
            clientes_rodrigo = clientes_rodrigo[['Conta' , 'Assessor Indicador']]
        if column_conta == 'Conta':
            dataframe = dataframe.merge(clientes_rodrigo, how='left', on=column_conta)
        else:
            dataframe = dataframe.merge(clientes_rodrigo, how='left', left_on=column_conta, right_on='Conta')
            dataframe.drop(['Conta'], axis=1, inplace=True)

        null = dataframe['Assessor Indicador'].isnull().to_numpy()
        clientes = dataframe[column_conta].to_numpy()
        
        for i, *_ in enumerate(dataframe['Assessor Indicador'].to_numpy()):        
            is_null = null[i]
            if is_null:
                
                if column_assessor != None:
                    assessor_indicador = dataframe.loc[i, column_assessor]
                    dataframe.loc[i,'Assessor Indicador'] = assessor_indicador
        
                elif column_assessor == None:
                    cliente_selecionado = clientes[i]
                    mask_cliente = positivador['Cliente'] == cliente_selecionado
                    assessor_indicador = positivador.loc[mask_cliente , 'Assessor'].iloc[0]
                    dataframe.loc[i,'Assessor Indicador'] = assessor_indicador

        new_dataframe = dataframe.copy()
        
        if inplace: setattr(self, 'dataframe', new_dataframe)
        return new_dataframe

    def add_assessor_relacionamento(self, clientes_rodrigo, column_conta='Cliente', positivador = None, column_assessor='Assessor', assessores_com_A = False, inplace=True):
        """Essa função adiciona a coluna de assessor indicador a um dataframe com coluna de contas"""

        dataframe = self.dataframe

        if assessores_com_A == False:
            clientes_rodrigo['Assessor Relacionamento'] = clientes_rodrigo['Assessor Relacionamento'].str.strip('A')
            clientes_rodrigo['Assessor Relacionamento'] = clientes_rodrigo['Assessor Relacionamento'].str.replace('tendimento Fatorial', 'Atendimento Fatorial')
        clientes_rodrigo = clientes_rodrigo[['Conta' , 'Assessor Relacionamento']]
        if column_conta == 'Conta':
            dataframe = dataframe.merge(clientes_rodrigo, how='left', on=column_conta)
        else:
            dataframe = dataframe.merge(clientes_rodrigo, how='left', left_on=column_conta, right_on='Conta')
            dataframe.drop(['Conta'], axis=1, inplace=True)

        null = dataframe['Assessor Relacionamento'].isnull().to_numpy()
        clientes = dataframe[column_conta].to_numpy()
        
        for i, *_ in enumerate(dataframe['Assessor Relacionamento'].to_numpy()):        
            is_null = null[i]
            if is_null:
                
                if column_assessor != None:
                    assessor_relacionamento = dataframe.loc[i, column_assessor]
                    dataframe.loc[i,'Assessor Relacionamento'] = assessor_relacionamento
        
                elif column_assessor == None:
                    cliente_selecionado = clientes[i]
                    mask_cliente = positivador['Cliente'] == cliente_selecionado
                    try:
                        assessor_relacionamento = positivador.loc[mask_cliente , 'Assessor'].iloc[0]
                    except:
                        assessor_relacionamento = 'Não consta'
                    
                    dataframe.loc[i,'Assessor Relacionamento'] = assessor_relacionamento
        
        new_dataframe = dataframe.copy()
        
        if inplace: setattr(self, 'dataframe', new_dataframe)
        return new_dataframe

    def reorder_columns(self, col_name, position, inplace=True):
        dataframe = self.dataframe
        """Reorder a dataframe's column.
        Args:
            dataframe (pd.DataFrame): dataframe to use
            col_name (string): column name to move
            position (0-indexed position): where to relocate column to
        Returns:
            pd.DataFrame: re-assigned dataframe
        """
        temp_col = dataframe[col_name]
        dataframe = dataframe.drop(columns=[col_name])
        dataframe.insert(loc=position, column=col_name, value=temp_col)
        
        new_dataframe = dataframe.copy()
        
        if inplace: setattr(self, 'dataframe', new_dataframe)
        return new_dataframe

    def add_nome_cliente(self, suitability, column_conta='Cliente', inplace=True):
        """Essa função adiciona o nome de um cliente, com base na Suitability"""
        dataframe = self.dataframe
        suitability = suitability [['CodigoBolsa', 'NomeCliente']]
        dataframe = dataframe.merge(suitability, how='left', left_on=column_conta, right_on='CodigoBolsa')
        dataframe = dataframe.drop('CodigoBolsa', axis = 1)

        new_dataframe = dataframe.copy()

        if inplace: setattr(self, 'dataframe', new_dataframe)
        return new_dataframe

    def add_nome_assessor(self, assessores, column_assessor='Assessor', inplace=True):
        """Essa função adiciona o nome do assessor, com base na assessores leal pablo"""
        dataframe = self.dataframe
        assessores = assessores [['Código assessor', 'Nome assessor']]
        dataframe = dataframe.merge(assessores, how='left', left_on=column_assessor, right_on='Código assessor')
        if column_assessor != 'Código assessor':
            dataframe = dataframe.drop('Código assessor', axis = 1)
        dataframe['Nome assessor'].fillna(dataframe[column_assessor], inplace=True)

        new_dataframe = dataframe.copy()

        if inplace: setattr(self, 'dataframe', new_dataframe)
        return new_dataframe

class Data:
    def __init__(self, data):
        self.cod_data = data
        self.day = int(data[:2])
        self.month = int(data[2:4])
        self.year = int(data[4:])
        self.datetime = date(
            year = 2000 + self.year,
            month = self.month,
            day=self.day
        )
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        self.text_month = meses[self.month - 1]

class Get:

    def __init__(self): 
        pass
    
    def assessores(): 
        df = import_excel_data('Assessores leal_Pablo.xlsx', '/Fatorial/Inteligência/Codigos/bases_dados/', dbx=dbx)
        df['Código assessor'] = df['Código assessor'].astype(str)
        return df

    def captacao_total():
        df = import_excel_data('captacao_2022.xlsx', dbx=dbx)
        return df
    
    def novos_transf_total():
        df = import_excel_data('novos_transf_2022.xlsx', dbx=dbx)
        df['Assessor Indicador'] = df['Assessor Indicador'].astype(str)
        df['Cliente'] = df['Cliente'].astype(str)
        return df
    
    def receitas_total(): 
        return import_excel_data('receitas_2022.xlsx', sheet_name='Resumo Tags', dbx=dbx)
    
    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def receitas_cliente(): 
        df = import_excel_data('receitas_clientes_2022.xlsx', dbx=dbx)
        df['Cliente'] = df['Cliente'].astype(str)
        return df
    
    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def captacao_cliente(): 
        df = import_excel_data('captacao_cliente_2022.xlsx', dbx=dbx)
        df['Cliente'] = df['Cliente'].astype(str)
        return df

    def carteira_total(): 
        carteiras = import_excel_data('carteira_2022.xlsx', dbx=dbx)
        carteiras['Produto'].replace('Tesouro Direto','Renda Fixa', inplace=True)
        carteiras['Produto'].replace('Renda Variável','Mesa RV', inplace=True)
        return carteiras

    def roa_total(): 
        roa = import_excel_data('ROA_2022.xlsx', dbx=dbx)
        roa['Código assessor'] = roa['Código assessor'].astype(str)
        return roa
    
    def aniversario(): 
        aniversario = import_excel_data('tabela_completa.xlsx', '/Fatorial/Inteligência/Codigos/aniversario_diario/', dbx=dbx)
        aniversario['Data de Aniversário'] = aniversario['Data de Aniversário'].apply(lambda x: x.strftime('%Y-%m-%d'))
        return aniversario
    
    def superranking_total(): 
        return import_excel_data('SuperRanking_Acumulado.xlsx', dbx=dbx)

    def positivador(data_hoje):
        try:
            
            df = import_excel_data(f'positivador_{data_hoje}.xlsx', '/Fatorial/Inteligência/Codigos/captacao_diario/', dbx=dbx, skip_rows=2)
        
        except ApiError:
            
            obj = Data(data_hoje)

            mes = str(obj.text_month)
            ano = '20' + str(obj.year)

            df =  import_excel_data(f'positivador_{data_hoje}.xlsx', f'/Fatorial/Inteligência/Codigos/captacao_diario/arquivos/{ano}/{mes}/', dbx=dbx, skip_rows=2)

        df['Cliente'] = df['Cliente'].astype(str)
        df['Assessor'] = df['Assessor'].astype(str)

        return df

    def suitability(): 
        df = import_excel_data('Suitability Acumulada.xlsx', '/Fatorial/Inteligência/Codigos/bases_dados/', dbx=dbx) 
        df['CodigoBolsa'] = df['CodigoBolsa'].astype(str)
        return df
    
    def transferencia(data_hoje):
        try:
            
            df = import_excel_data(f'transferencias_{data_hoje}.xlsx', '/Fatorial/Inteligência/Codigos/captacao_diario/', dbx=dbx)
        
        except ApiError:
            
            obj = Data(data_hoje)

            mes = str(obj.text_month)
            ano = '20' + str(obj.year)

            df =  import_excel_data(f'transferencias_{data_hoje}.xlsx', f'/Fatorial/Inteligência/Codigos/captacao_diario/arquivos/{ano}/{mes}/', dbx=dbx)

        df['Cliente'] = df['Cliente'].astype(str)

        return df
    
    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def diversificador(data_hoje):
        
        diversificador = import_excel_data(f'diversificacao_{data_hoje}.xlsx', r'/Fatorial/Inteligência/Codigos/COE/arquivos/', dbx=dbx, skip_rows=2)
        
        diversificador['Cliente'] = diversificador['Cliente'].astype(str)
        diversificador['Assessor'] = diversificador['Assessor'].astype(str)
        
        return diversificador
    
    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def captacao(data_hoje, sheet_name='Resumo'):
        try:
            
            df = import_excel_data(f'captacao_{data_hoje}.xlsx', '/Fatorial/Inteligência/Codigos/captacao_diario/', dbx=dbx, sheet_name=sheet_name)
        
        except ApiError:
            
            obj = Data(data_hoje)

            mes = str(obj.text_month)
            ano = '20' + str(obj.year)

            df =  import_excel_data(f'captacao_{data_hoje}.xlsx', f'/Fatorial/Inteligência/Codigos/captacao_diario/arquivos/{ano}/{mes}/', dbx=dbx, sheet_name=sheet_name)

        if sheet_name == 'Resumo':
            df['Código assessor'] = df['Código assessor'].astype(str)

        elif sheet_name=='Positivador M' or sheet_name=='Novos + Transf' or sheet_name == 'Perdidos':
            df['Cliente'] = df['Cliente'].astype(str)
            df['Assessor'] = df['Assessor'].astype(str)

        return df
    
    def clientes_rodrigo(mes=None, ano='2022'): 
        if mes == None:
            df = import_excel_data('Clientes do Rodrigo.xlsx', '/Coisas da Fatorial/', dbx=dbx, sheet_name='Troca')
        else:
            df = import_excel_data(f'Clientes Rodrigo {mes}.xlsx', f'/Fatorial/Inteligência/Codigos/clientes_rodrigo/{ano}/', dbx=dbx)
        
        df['Conta'] = df['Conta'].astype(str)

        return df

    def coe_diario(mes):
        df = import_excel_data(f'COE_{mes}.xlsx', '/Fatorial/Inteligência/Codigos/COE/Análise de COE/', dbx=dbx)
        df['Cliente'] = df['Cliente'].astype(str)
        return df
    
    def base_b2c(mes, celula):
        dataframe = import_excel_data(f'distribuicao_clientes_{str.lower(celula)}_{str.lower(mes)}.xlsx', '/Fatorial/Inteligência/Codigos/Relatórios Digital/Base Clientes/', dbx=dbx, sheet_name='Ativo')
        dataframe = dataframe[['Assessor', 'Cliente', 'Responsável']]
        dataframe['Cliente'] = dataframe['Cliente'].astype(str)
        return dataframe
    
    def nps_anual(year):
        envios = import_excel_data('Lista de Envios 2022.xlsx', f'/Fatorial/Inteligência/Codigos/NPS/Anual/{year}/', skip_rows=2, dbx=dbx)
        ranking_assessores = import_excel_data('Ranking Assessores 2022.xlsx', f'/Fatorial/Inteligência/Codigos/NPS/Anual/{year}/', skip_rows=4, dbx=dbx)
        ranking_onboarding = import_excel_data('Ranking Onboarding 2022.xlsx', f'/Fatorial/Inteligência/Codigos/NPS/Anual/{year}/', skip_rows=4, dbx=dbx)

        return envios, ranking_assessores, ranking_onboarding

    def clientes_antigos(): 
        
        clientes_char = import_excel_data('Clientes Char.xlsx', f'/Fatorial/Inteligência/Codigos/bases_dados/Bases de assessores antigos/', dbx=dbx)
        clientes_thieme = import_excel_data('Clientes Thieme.xlsx', f'/Fatorial/Inteligência/Codigos/bases_dados/Bases de assessores antigos/', dbx=dbx)

        return clientes_char, clientes_thieme

    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def receitas(dia):
        data_obj = Data(dia)
        mes = data_obj.text_month
        ano = '20' + str(data_obj.year)
        
        dataframe = import_csv_data(
            'dados_comissão_' + (str.lower(mes)).replace('ç', 'c') + r'.csv',
            '/Fatorial/Inteligência/Codigos/Comissões/Receitas/Bases SplitC/' + ano + '/')
        
        dataframe['Assessor Dono'] = dataframe['Assessor Dono'].str.title()
        dataframe['Cliente'] = dataframe['Cliente'].astype(str)
        return dataframe

    def tags():
        return import_excel_data('Tags x Categorias.xlsx', '/Fatorial/Inteligência/Codigos/Comissões/Bases de dados/')

    def pesquisas_nps():
        return import_excel_data('Relatório Pesquisas.xlsx', '/Fatorial/Inteligência/Codigos/NPS/Relatorios/')

    def prev_nps():
        return import_excel_data('Relatório Prev.xlsx', '/Fatorial/Inteligência/Codigos/NPS/Relatorios/')

    def ranking_nps():
        return import_excel_data('Relatório Ranking NPS.xlsx', '/Fatorial/Inteligência/Codigos/NPS/Relatorios/')
    
    def respostas_nps():
        return import_excel_data('Relatório Respostas.xlsx', '/Fatorial/Inteligência/Codigos/NPS/Relatorios/')

    def metas_2023(sheet_name='Assessores'):
        return import_excel_data('Metas 2023.xlsx')

class LandingPage:
    
    @st.cache(ttl=60*30, max_entries=50)
    def filter_receita(receita, assessores, clientes_rodrigo):
        mask_ajustes = receita['Categoria'].isin(['Ajuste', 'Ajustes XP', 'Outros Ajustes', 'Incentivo Comercial', 'Complemento de Comissão Mínima', 'Desconto de Transferência de Clientes', 'Incentivo', 'Erro Operacional'])
        receita = receita[~mask_ajustes]

        receita['Assessor Dono'] = receita['Assessor Dono'].str.upper().str.lstrip('A')
        receita['Assessor Dono'].replace("DRIANO MENEGUITE", 'ADRIANO MENEGUITE', inplace=True)
        receita['Assessor Dono'].replace("LINY MANZIERI", 'ALINY MANZIERI', inplace=True)
        receita['Assessor Dono'].replace("TENDIMENTO FATORIAL", 'ATENDIMENTO FATORIAL', inplace=True)
        
        receita = Dataframe(receita)

        receita.add_nome_assessor(assessores, 'Assessor Dono')
        receita.add_assessor_indicador(clientes_rodrigo, column_assessor='Assessor Dono')

        receita = receita.dataframe

        return receita

    @st.cache(ttl=60*30, max_entries=50)
    def get_novos_transf_display(novos_transf, suitability):
    
        novos_transf_display = novos_transf[['Cliente', 'Net Em M', 'Transferência?']]
        
        novos_transf_display = novos_transf_display.merge(suitability[['CodigoBolsa', 'NomeCliente']], how='left', left_on='Cliente', right_on='CodigoBolsa')
        
        novos_transf_display = novos_transf_display[['Cliente', 'NomeCliente', 'Net Em M', 'Transferência?']]
        
        novos_transf_display.rename(columns={'Cliente': 'Código','Net Em M':'PL de Entrada', 'NomeCliente':'Cliente'}, inplace=True)
        
        novos_transf_display.sort_values('PL de Entrada', inplace=True, ascending=False)

        novos_transf_display['PL de Entrada'] = novos_transf_display['PL de Entrada'].apply(lambda x: 'R$ {:,.2f}'.format(x))

        return novos_transf_display

    @st.cache(ttl=60*30, max_entries=50)
    def get_perdidos_display(perdidos, suitability):
        
        perdidos_display = perdidos[['Cliente', 'Net Em M']]
        
        perdidos_display = perdidos_display.merge(suitability[['CodigoBolsa', 'NomeCliente']], how='left', left_on='Cliente', right_on='CodigoBolsa')
        
        perdidos_display = perdidos_display[['Cliente', 'NomeCliente', 'Net Em M']]
        
        perdidos_display.rename(columns={'Cliente': 'Código','Net Em M':'PL de Saída', 'NomeCliente':'Cliente'}, inplace=True)

        perdidos_display.sort_values('PL de Saída', inplace=True, ascending=False)

        perdidos_display['PL de Saída'] = perdidos_display['PL de Saída'].apply(lambda x: 'R$ {:,.2f}'.format(x))

        return perdidos_display

    @st.cache(ttl=60*30, max_entries=50)
    def get_receitas_tag_clientes(receita, tags, categorias, positivador):
        df_cliente = receita.groupby('Cliente').sum()[['Valor Bruto Recebido']].reset_index(drop=False)
        df_tags = receita.merge(tags, how='left', on='Categoria').groupby('Centro de Custo').sum()[['Valor Bruto Recebido']].sort_values('Valor Bruto Recebido', ascending=False)

        df_cliente = df_cliente.merge(categorias, how='left', on='Cliente')

        df_cliente = df_cliente.merge(positivador[['Cliente', 'Net Em M']], how='left', on='Cliente')
        
        mask_faixa_1 = df_cliente['Net Em M'] > 0
        mask_faixa_2 = df_cliente['Net Em M'] > 100000
        mask_faixa_3 = df_cliente['Net Em M'] > 300000
        mask_faixa_4 = df_cliente['Net Em M'] > 500000
        mask_faixa_5 = df_cliente['Net Em M'] > 1000000
        mask_faixa_6 = df_cliente['Net Em M'] > 3000000

        df_cliente['Faixa'] = 'vii. Fora XP'

        df_cliente.loc[mask_faixa_1, 'Faixa'] = 'i. < 100k'
        df_cliente.loc[mask_faixa_2, 'Faixa'] = 'ii. 100k-300k'
        df_cliente.loc[mask_faixa_3, 'Faixa'] = 'iii. 300k-500k'
        df_cliente.loc[mask_faixa_4, 'Faixa'] = 'iv. 500k-1MM'
        df_cliente.loc[mask_faixa_5, 'Faixa'] = 'v. 1MM-3MM'
        df_cliente.loc[mask_faixa_6, 'Faixa'] = 'vi. +3MM'

        return df_cliente, df_tags

def to_excel(df, index=True, sheet_names=[]):

    if type(df) != list:
        df = [df]
    
    if sheet_names == []:
        sheet_names = [f'Sheet{i+1}' for i, *_ in enumerate(df)]
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    for i, dataframe in enumerate(df):
        print(dataframe)
        dataframe.to_excel(writer, index=index, sheet_name=sheet_names[i])
    writer.save()
    return buffer

def espacamento(n, self):
    for i in range(n): self.write('')

def stream_dropbox_file(path, dbx):
    _,res=dbx.files_download(path)
    with closing(res) as result:
        byte_data=result.content
        return io.BytesIO(byte_data)

def import_excel_data(path, file_path= '/Fatorial/Inteligência/Codigos/Bases de Performance/Base Dados/', sheet_name=None, dbx=dbx, skip_rows=0):
    file_stream = stream_dropbox_file(file_path + path, dbx)
    if sheet_name != None:
        data = pd.read_excel(file_stream, sheet_name = sheet_name, skiprows=skip_rows)
    else:
        data = pd.read_excel(file_stream, skiprows=skip_rows)
    return data

def import_csv_data(path, file_path= '/Fatorial/Inteligência/Codigos/Bases de Performance/Base Dados/', decimal=',', sep=';', dbx=dbx, skip_rows=0):
    file_stream = stream_dropbox_file(file_path + path, dbx)
    data = pd.read_csv(file_stream, decimal=decimal, sep=sep)
    return data

def captacao(posi_novo, posi_velho, clientes_rodrigo, assessores, lista_transf, clientes_novos_ontem, suitability, data_hoje, responsavel_digital = "Atendimento Fatorial", year=2022, gera_excel = True):

    """Tanto separando os assessores em times, quanto analisando individualmente, esse código gera um
    relatório diário, com base nos arquivos da XP, reportando a ccaptação e o AUM dos assessores."""

    import pandas as pd

    #diretorio arquivo final

    clientes_rodrigo = clientes_rodrigo.loc[:, ['Conta', 'Assessor Relacionamento']]

    #montando tabela clientes perdidos ----------------------------------------------------------------------------------------------------------------------------

    #encontrando quais são os clientes perdidos
    posi_velho['Clientes perdidos'] = posi_velho['Cliente'].where(posi_velho['Cliente'].isin(posi_novo['Cliente']) == True)

    #renomeando os valores: na -> "Saiu" ; código cliente -> "Permanece"
    posi_velho['Clientes perdidos'].fillna('Saiu' , inplace = True)

    posi_velho.loc[posi_velho['Clientes perdidos'] != 'Saiu' , 'Clientes perdidos'] = 'Permanece'

    #montagem do dataframe
    tabela_perdidos = posi_velho.loc[posi_velho['Clientes perdidos'] == 'Saiu' , :]

    #criação de coluna de assessor correto
    tabela_perdidos = tabela_perdidos.merge(clientes_rodrigo , left_on='Cliente' , right_on='Conta' , how= 'left')

    tabela_perdidos['Assessor Relacionamento'].fillna(tabela_perdidos['Assessor'] , inplace = True)

    tabela_perdidos.rename(columns={'Assessor Relacionamento' : 'Assessor correto'} , inplace= True)

    del tabela_perdidos['Conta']

    tabela_perdidos.loc[tabela_perdidos['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    # montando tabela de clientes velhos ----------------------------------------------------------------------------------------------------------------------------

    #encontrando quais são os clientes velhos
    #posi_novo['Status conta'] = posi_novo['Cliente'].where(posi_novo['Cliente'].isin(posi_velho['Cliente']) == True)

    posi_novo.loc [posi_novo["Cliente"].isin (posi_velho['Cliente']),"Status conta"] = 'conta velha'

    posi_novo['Status conta'].fillna('conta nova' , inplace = True)

    posi_novo.drop_duplicates (subset = "Cliente",inplace=True)

    #seleção das contas velhas
    tabela_velhos = posi_novo.loc[posi_novo['Status conta'] == 'conta velha' , :]

    #criação da coluna de assessor correto
    tabela_velhos = pd.merge(tabela_velhos , clientes_rodrigo , left_on= 'Cliente' , right_on= 'Conta' , how= 'left')

    tabela_velhos['Assessor Relacionamento'].fillna(tabela_velhos['Assessor'] , inplace = True)

    tabela_velhos.rename(columns={'Assessor Relacionamento':'Assessor correto'} , inplace= True)

    del tabela_velhos['Conta']

    tabela_velhos.loc[tabela_velhos['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    # montando tabela de clientes novos e transferencias ----------------------------------------------------------------------------------------------------------------------------

    #tabela clientes novos + transferencias
    tabela_novos_transf = posi_novo.loc[posi_novo['Status conta'] == 'conta nova' , :]


    #identificando quais são as transferências
    tabela_novos_transf.loc[: ,'Transferência?'] = tabela_novos_transf.loc[: , 'Cliente'].where(tabela_novos_transf.loc[: , 'Cliente'].isin(lista_transf.loc[: , 'Cliente']) == True)

    tabela_novos_transf['Transferência?'].fillna('Não' , inplace = True)

    tabela_novos_transf.loc[tabela_novos_transf['Transferência?'] !='Não' , 'Transferência?'] = 'Sim'

    tabela_novos_transf.loc[tabela_novos_transf['Net em M-1'] > 0 , 'Transferência?'] = 'Sim'

    #tabela clientes novos
    tabela_novos = tabela_novos_transf.loc[tabela_novos_transf['Transferência?'] == 'Não' , :]

    #cliente rodrigo para os novos
    tabela_novos = pd.merge(tabela_novos , clientes_rodrigo , left_on= 'Cliente' , right_on= 'Conta' , how = 'left')

    tabela_novos['Assessor Relacionamento'].fillna(tabela_novos['Assessor'] , inplace = True)

    tabela_novos.rename(columns = {'Assessor Relacionamento' : 'Assessor correto'} , inplace= True)

    del tabela_novos['Conta']

    tabela_novos.loc[tabela_novos['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    #tabela transferências
    tabela_transf = tabela_novos_transf.loc[tabela_novos_transf['Transferência?'] == 'Sim' , :]

    #cliente rodrigo para as transferências
    tabela_transf = pd.merge(tabela_transf , clientes_rodrigo , left_on='Cliente' , right_on='Conta' , how='left')

    tabela_transf['Assessor Relacionamento'].fillna(tabela_transf['Assessor'] , inplace = True)

    tabela_transf.rename(columns = {'Assessor Relacionamento' : 'Assessor correto'} , inplace = True)

    del tabela_transf['Conta']

    tabela_transf.loc[tabela_transf['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    #montando dados para de captação ----------------------------------------------------------------------------------------------------------------------------------

    #dados contas velhas
    dados_velhos = tabela_velhos.loc[: , ['Cliente' , 'Assessor correto' , 'Captação Líquida em M']]

    dados_velhos = dados_velhos.astype({'Assessor correto': str})

    #dados contas efetivamente novas
    dados_novos = tabela_novos.loc[: , ['Cliente' , 'Assessor correto' , 'Captação Líquida em M']]

    dados_novos = dados_novos.astype({'Assessor correto': str})

    #dados contas transferências (valor a ser considerado : Soma de NET M-1 e Captação Líquida)
    dados_transf = tabela_transf.loc[: , ['Cliente' , 'Assessor correto' , 'Captação Líquida em M' , 'Net em M-1']]

    dados_transf['Total transferências'] = dados_transf['Captação Líquida em M'] + dados_transf['Net em M-1']

    dados_transf = dados_transf.astype({'Assessor correto': str})

    #dados contas perdidas (valor a ser considerado : Soma de Net em M)
    dados_perdidos = tabela_perdidos.loc[: , ['Cliente' , 'Assessor correto' , 'Net Em M' ]]

    dados_perdidos.loc[: , 'Total contas perdidas'] = dados_perdidos['Net Em M'] * -1

    dados_perdidos = dados_perdidos.astype({'Assessor correto': str})

    #transformando os dados em resumos -------------------------------------------------------------------------------------------------------------------------------------------------------

    #resumo das contas velhas
    resumo_velhos = dados_velhos.loc[: , ['Assessor correto' , 'Captação Líquida em M']].groupby('Assessor correto').sum()

    resumo_velhos.rename(columns = {'Captação Líquida em M' : 'Total conta velha'} , inplace = True)

    #resumo das contas efetivamente novas
    resumo_novos = dados_novos.loc[: , ['Assessor correto' , 'Captação Líquida em M']].groupby('Assessor correto').sum()

    resumo_novos.rename(columns = {'Captação Líquida em M' : 'Total conta nova'}, inplace = True)

    #resumo das transferências
    resumo_transf = dados_transf.loc[: , ['Assessor correto' , 'Total transferências']].groupby('Assessor correto').sum()

    #resumo contas perdidas
    resumo_perdidos = dados_perdidos.loc[: , ['Assessor correto' , 'Total contas perdidas']].groupby('Assessor correto').sum()

    #construção dos dados da carteira atual (base positivador M) ------------------------------------------------------------------------------------------------------------------------------------------------

    #criando dados base
    dados_carteira = posi_novo.loc[: , ['Assessor' , 'Cliente' , 'Net Em M']]

    #inserindo assessores corretos 
    dados_carteira = pd.merge(dados_carteira , clientes_rodrigo , left_on='Cliente' , right_on='Conta' , how='left')

    dados_carteira['Assessor Relacionamento'].fillna(dados_carteira['Assessor'] , inplace = True)

    dados_carteira.rename(columns = {'Assessor Relacionamento' : 'Assessor correto'} , inplace = True)

    del dados_carteira['Conta']

    dados_carteira.loc[dados_carteira['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    dados_carteira = dados_carteira.astype({'Assessor correto': str})

    #retirando os clientes zerados da base

    dados_carteira = dados_carteira.loc[dados_carteira['Net Em M'] != 0 , :]

    #achando a quantidade de clientes que cada assessor possui

    dados_carteira_qtd = dados_carteira.loc[: , ['Assessor correto' , 'Cliente']].groupby('Assessor correto').count()

    #achando o somatório de NET para cada assessor

    dados_carteira_net = dados_carteira.loc[: , ['Assessor correto' , 'Net Em M']].groupby('Assessor correto').sum()

    #juntando as informações e achando o ticket médio

    dados_carteira_assessor = pd.merge(dados_carteira_qtd , dados_carteira_net , left_index=True , right_index=True , how= 'left')

    dados_carteira_assessor.loc[: , 'Ticket Médio'] = dados_carteira_assessor['Net Em M'] / dados_carteira_assessor['Cliente']

    dados_carteira_assessor.rename(columns={'Cliente' : 'Qtd Clientes n/ zerados'} , inplace=True)

    #montando dados sob o ponto de vista da XP

    dados_carteira_xp = posi_novo.loc[posi_novo['Net Em M'] != 0 , ['Assessor' , 'Cliente' , 'Net Em M']]

    dados_carteira_xp = dados_carteira_xp.loc[: , ['Assessor' , 'Cliente']].groupby('Assessor').count()

    variavel = posi_novo[['Assessor' , 'Net Em M']].groupby('Assessor').sum()

    dados_carteira_xp = pd.merge(dados_carteira_xp , posi_novo[['Assessor' , 'Net Em M']].groupby('Assessor').sum() , how='left' , on='Assessor')

    dados_carteira_xp.rename(columns={'Cliente':'Qtd Clientes XP' , 'Net Em M' : 'NET XP'} , inplace=True)

    dados_carteira_xp.reset_index(inplace=True)

    dados_carteira_xp = dados_carteira_xp.astype({'Assessor':str})

    #montargem do tabelão de captação -------------------------------------------------------------------------------------------------------------------------------

    tabela_captacao = pd.merge(assessores, resumo_velhos , left_on='Código assessor' , right_index= True , how= 'left')

    tabela_captacao = pd.merge(tabela_captacao , resumo_novos , left_on='Código assessor' , right_index= True , how = 'left')

    tabela_captacao = pd.merge(tabela_captacao , resumo_transf , left_on = 'Código assessor' , right_index= True , how = 'left')

    tabela_captacao = pd.merge(tabela_captacao , resumo_perdidos , left_on = 'Código assessor' , right_index = True , how = 'left')

    tabela_captacao['Captação Líquida'] = tabela_captacao.sum(axis = 1)

    tabela_captacao = pd.merge(tabela_captacao , dados_carteira_assessor , left_on='Código assessor' , right_index=True , how='left')

    tabela_captacao = pd.merge(tabela_captacao , dados_carteira_xp , how='left' , left_on='Código assessor' , right_on='Assessor')

    del tabela_captacao['Assessor']

    for n in tabela_captacao.columns:
        tabela_captacao[n].fillna(0 , inplace = True)

    #Linha total da tabela captação assessores

    tabela_captacao.set_index('Código assessor', inplace = True)

    tabela_captacao.loc['Total Fatorial'] = tabela_captacao[['Total conta velha' , 'Total conta nova' , 'Total transferências' , 'Total contas perdidas' , 'Captação Líquida','Qtd Clientes n/ zerados','Net Em M' , 'Qtd Clientes XP','NET XP']].sum()

    tabela_captacao.reset_index(inplace=True)

    tabela_captacao['Ticket Médio'].iloc[-1] = tabela_captacao['Net Em M'].iloc[-1] / tabela_captacao['Qtd Clientes n/ zerados'].iloc[-1]

    tabela_captacao.fillna('Total Fatorial',inplace=True)
    
    #Tira do resumo quem não tem patrimonio

    mask_sem_net = tabela_captacao['Net Em M'] == 0

    mask_sem_net_xp = tabela_captacao['NET XP'] == 0

    mask_sem_capt = tabela_captacao['Captação Líquida'] == 0

    tabela_captacao = tabela_captacao[~(mask_sem_net & mask_sem_capt & mask_sem_net_xp)]


    #montagem por células

    tabela_celulas = tabela_captacao.loc[: , tabela_captacao.columns.isin(['Nome assessor','Ticket Médio']) == False].groupby('Time').sum()

    tabela_celulas.loc[: , 'Ticket Médio'] = tabela_celulas['Net Em M'] / tabela_celulas['Qtd Clientes n/ zerados']

    qtd_assessores = assessores.loc[: , ['Nome assessor','Time']].groupby('Time').count()

    tabela_celulas = pd.merge(tabela_celulas , qtd_assessores , left_index=True , right_index=True , how='left')

    tabela_celulas.loc['Total Fatorial','Nome assessor'] = tabela_celulas['Nome assessor'].sum()

    tabela_celulas['Captação / Assessor'] = tabela_celulas['Captação Líquida'] / tabela_celulas['Nome assessor']

    tabela_celulas = tabela_celulas.loc[: , ['Total conta velha' , 'Total conta nova' , 'Total transferências' , 'Total contas perdidas' , 'Captação Líquida' , 'Captação / Assessor' , 'Qtd Clientes n/ zerados' , 'Net Em M' , 'Ticket Médio', 'Qtd Clientes XP','NET XP']]

    tabela_celulas.reset_index(inplace=True)

    #criando coluna de assessores corretos no positivador novo

    posi_novo = pd.merge(posi_novo , clientes_rodrigo , left_on = 'Cliente' , right_on = 'Conta' , how = 'left')

    posi_novo['Assessor Relacionamento'].fillna(posi_novo['Assessor'] , inplace = True)

    posi_novo.rename(columns={'Assessor Relacionamento': 'Assessor correto'} , inplace=True)

    del posi_novo['Conta']

    posi_novo.loc[posi_novo['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    posi_novo = posi_novo.astype({'Assessor correto': str})

    # clientes novos no dia D ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #pegando a lista acumuladados clientes novos que entraram

    clientes_novos_acum = tabela_novos_transf.loc[: , ['Cliente' , 'Assessor' ,'Aplicação Financeira Declarada' , 'Data de Nascimento' ,'Transferência?']]

    #cruzando com os clientes rodrigo

    clientes_novos_acum = pd.merge(clientes_novos_acum , clientes_rodrigo , left_on='Cliente' , right_on='Conta' , how='left')

    clientes_novos_acum['Assessor Relacionamento'].fillna(clientes_novos_acum['Assessor'] , inplace = True)

    clientes_novos_acum.rename(columns = {'Assessor Relacionamento' : 'Assessor correto'} , inplace = True)

    del clientes_novos_acum['Conta']

    clientes_novos_acum.loc[clientes_novos_acum['Assessor correto'] == '1618' , 'Assessor correto'] = responsavel_digital

    clientes_novos_acum = clientes_novos_acum.astype({'Assessor correto': str})

    #nome do cliente

    clientes_novos_acum = pd.merge(clientes_novos_acum ,suitability[['CodigoBolsa' , 'NomeCliente']] , how='left' , left_on='Cliente' , right_on='CodigoBolsa' )

    del clientes_novos_acum['CodigoBolsa']

    clientes_novos_acum.rename(columns={'NomeCliente':'Nome'},inplace=True)

    clientes_novos_acum['Nome'].fillna('Não encontrado' , inplace=True)


    # lista de clientes novos acumulados no relatório D-1

    clientes_novos_ontem = clientes_novos_ontem.loc[: , ['Cliente' , 'Transferência?']]

    clientes_novos_ontem['Presente'] = 'Ontem'

    # cruzando os clientes novos de ontem e os de hoje

    clientes_novos_acum = pd.merge(clientes_novos_acum , clientes_novos_ontem[['Cliente' , 'Presente']] , how='left' , on='Cliente')

    clientes_novos_acum['Presente'].fillna('Hoje' , inplace=True)

    #colocando nome dos assessores

    clientes_novos_acum = pd.merge(clientes_novos_acum , assessores[['Código assessor','Nome assessor']] , how='left' , left_on='Assessor correto' , right_on='Código assessor')

    #colocando a profissão do cliente

    clientes_novos_acum = pd.merge(clientes_novos_acum , posi_novo[['Cliente','Profissão']] , how='left' , on='Cliente')

    # filtrando quais são os clientes de hoje

    clientes_novos_hj = clientes_novos_acum.loc[clientes_novos_acum['Presente']=='Hoje' , ['Cliente' , 'Nome' , 'Profissão' , 'Data de Nascimento' ,'Assessor correto' , 'Nome assessor' , 'Aplicação Financeira Declarada']]

    clientes_novos_hj.rename(columns = {'Assessor correto':'Assessor' , 'Aplicação Financeira Declarada':'PL Declarado'} , inplace=True)

    clientes_novos_hj.reset_index(inplace=True)

    if gera_excel == False:
        return tabela_captacao, tabela_transf

    #montar excel final -----------------------------------------------------------------------------------------------------------------------------------

    lista_tabelas = [
    (tabela_captacao, 'Resumo', 'Table Style Medium 2'),
    (tabela_celulas, 'Resumo times', 'Table Style Medium 2'),
    (tabela_velhos, 'Contas velhas', 'Table Style Medium 2'), 
    (tabela_novos, 'Contas novas', 'Table Style Medium 2'), 
    (tabela_transf, 'Transferêcnias', 'Table Style Medium 2'),
    (tabela_novos_transf, 'Novos + Transf', 'Table Style Medium 2'), 
    (clientes_novos_hj, 'Clientes novos D', 'Table Style Medium 2'), 
    (clientes_novos_acum, 'Clientes novos total', 'Table Style Medium 2'),
    (tabela_perdidos, 'Perdidos', 'Table Style Medium 2'), 
    (posi_novo, 'Positivador M', 'Table Style Medium 2'), 
    (dados_velhos, 'Dados velhos', 'Table Style Medium 2'),
    (dados_novos, 'Dados Novos', 'Table Style Medium 2'), 
    (dados_transf, 'Dados transferidos', 'Table Style Medium 2'), 
    (dados_perdidos, 'Dados perdidos', 'Table Style Medium 2'),
    ]

    # Com a lista de tabelas, gera as abas necessárias

    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter', datetime_format = 'dd/mm/yyyy')

    for tabela, nome_tabela, *_ in lista_tabelas:
        tabela.to_excel(writer , sheet_name= nome_tabela , index= False)

    # Formatação das tabelas

    for tabela, nome_aba, estilo in lista_tabelas:

        arquivo = writer.book
        aba = writer.sheets[nome_aba]
        
        colunas = [{'header':column} for column in tabela.columns ]
        (lin, col) = tabela.shape

        aba.add_table(0 , 0 , lin , col-1 , {
            'columns': colunas,
            'style': estilo, 
            'autofilter': False
            })
                

    writer.save()

    if tabela_captacao['NET XP'].sum() != tabela_captacao['Net Em M'].sum():
        st.write("Os valores de AUM não batem, verificar assessores") # REVISAR
    
    dbx.files_upload(
        f = buffer.getvalue(), 
        path = f'/Fatorial/Inteligência/Codigos/captacao_diario/captacao_{data_hoje}.xlsx', 
        mode=dropbox.files.WriteMode.overwrite)

    st.write("\nRelatório de Captação Salvo no Dropbox.")

    st.download_button(
        'Baixar o Relatório', 
        buffer,
        file_name = f'captacao_{data_hoje}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def export_files_captacao(data_hoje, data_ontem, data_mes_passado, responsavel_digital = "Atendimento Fatorial"):

    #importando positivador mês M 

    posi_novo = Get.positivador(data_hoje)

    posi_d1 = Get.positivador(data_ontem)

    posi_velho = Get.positivador(data_mes_passado)

    clientes_rodrigo = Get.clientes_rodrigo()
    clientes_rodrigo = clientes_rodrigo.loc[: , ['Conta' , 'Assessor Relacionamento', 'Assessor Indicador']]
    clientes_rodrigo.loc[clientes_rodrigo['Assessor Relacionamento'].isin(['Atendimento Fatorial']) == False , 'Assessor Relacionamento'] = pd.Series(clientes_rodrigo.loc[clientes_rodrigo['Assessor Relacionamento'].isin(['Atendimento Fatorial']) == False , 'Assessor Relacionamento']).str.lstrip('A')

    clientes_rodrigo = filtra_clientes_rodrigo(clientes_rodrigo)

    assessores = Get.assessores()

    lista_transf = Get.transferencia(data_hoje)
    lista_transf = lista_transf.loc[lista_transf['Status'] == 'CONCLUÍDO' , :]

    clientes_novos_ontem = Get.captacao(data_ontem, sheet_name='Novos + Transf')

    suitability = Get.suitability()

    return posi_novo, posi_d1, posi_velho, clientes_rodrigo, assessores, lista_transf, clientes_novos_ontem, suitability

def get_cod_data(data_hoje):
    if data_hoje.day < 10:
        day = '0' + str(data_hoje.day)
    else: 
        day = str(data_hoje.day)
    
    if data_hoje.month < 10:
        month = '0' + str(data_hoje.month)
    else: 
        month = str(data_hoje.month)

    year = str(data_hoje.year)[-2::]
    
    cod_data = day + month + year
    return cod_data

def get_fechamentos():
    return {
        'Dezembro21': '301221', 
        'Janeiro22': '310122', 
        'Fevereiro22': '250222', 
        'Março22': '310322', 
        'Abril22': '290422', 
        'Maio22': '310522', 
        'Junho22': '300622', 
        'Julho22': '280722',
        'Agosto22': '310822', 
        'Setembro22': '300922', 
        'Outubro22': '311022',
        'Novembro22': '301122',
        'Dezembro23':'291222'}

def get_meses():
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    return meses

def get_last_fechamento(data_hoje):
    
    fechamentos = get_fechamentos()

    obj = Data(data_hoje)
    mes_hoje = obj.text_month
    current_year = obj.year
    
    meses = get_meses()

    last_month = meses[meses.index(mes_hoje)-1]

    if mes_hoje == 'Janeiro':
        year_last_month = current_year - 1
    else:
        year_last_month = current_year

    return fechamentos[last_month + str(current_year)]
            
def aniversario(data_hoje, data_ontem, ano_corrente=2023, enviar_email=False):

    # Importando Base de Dados

    # Filtrando Código, Nome e Email e Relacionando com Positivador, para ter a data de Nascimento 
    # É necessário atualizar as versões das planilhas

    suitability = Get.suitability()
    positivador = Get.positivador(data_hoje)
    positivador_ontem = Get.positivador(data_ontem)
    clientes_rodrigo = Get.clientes_rodrigo()
    captacao_hj = Get.captacao(data_hoje, sheet_name="Positivador M")
    assessores_leal = Get.assessores()

    assessor_indicador = clientes_rodrigo.copy ()
    assessores = assessores_leal.copy()

    clientes_rodrigo = clientes_rodrigo [["Conta","Assessor Relacionamento"]]
    clientes_rodrigo.rename (columns={"Conta":"Cliente"},inplace=True)

    suitability = suitability [["CodigoBolsa","NomeCliente","EmailCliente"]]
    positivador = positivador[["Assessor","Cliente","Data de Nascimento"]]
    positivador_ontem = positivador_ontem[["Assessor","Cliente","Data de Nascimento"]]

    positivador.dropna(subset=['Data de Nascimento'], inplace=True)

    suitability.rename (columns={"CodigoBolsa":"Cliente"},inplace=True)

    tabela_completa = pd.merge (suitability,positivador,how="inner",on="Cliente")

    tabela_completa ["Data de Aniversário"] = tabela_completa ["Data de Nascimento"].apply (lambda x: date (ano_corrente,x.month,x.day) ).astype (np.datetime64)

    tabela_completa.drop ("Data de Nascimento",axis=1,inplace=True)

    tabela_completa ["Data Aviso: 10 Dias de Antecedência"] = tabela_completa ["Data de Aniversário"] - timedelta (days=10)

    dia_de_hoje = date.today ().strftime ("%Y-%m-%d")

    tabela_aviso = tabela_completa.loc [tabela_completa["Data Aviso: 10 Dias de Antecedência"]==dia_de_hoje,:]

    tabela_aviso = pd.merge (tabela_aviso,clientes_rodrigo,how="left",on="Cliente")

    tabela_aviso ["Assessor Relacionamento"].fillna (tabela_aviso["Assessor"],inplace=True)

    tabela_aviso.drop ("Assessor",axis=1,inplace=True)

    tabela_aviso ["Assessor Relacionamento"] = tabela_aviso ["Assessor Relacionamento"].astype (str)

    tabela_aviso.loc [tabela_aviso["Assessor Relacionamento"]!="Atendimento Fatorial","Assessor Relacionamento"] = tabela_aviso.loc [tabela_aviso["Assessor Relacionamento"]!="Atendimento Fatorial","Assessor Relacionamento"].apply (lambda x: x.replace ("A",""))

    assessores_leal ["Código assessor"] = assessores_leal ["Código assessor"].astype (str)  

    tabela_aviso = pd.merge (tabela_aviso,assessores_leal,how="left",left_on="Assessor Relacionamento",right_on="Código assessor")

    tabela_aviso.drop (["Código assessor","Time"],axis=1,inplace=True)

    tabela_aviso ["Nome assessor"].fillna ("Atendimento Fatorial",inplace=True)

    captacao_hj.rename (columns={"Assessor correto":"Assessor Relacionamento"},inplace=True)

    captacao_hj ["Assessor Relacionamento"] = captacao_hj ["Assessor Relacionamento"].astype (str)

    tabela_aviso = pd.merge (tabela_aviso,captacao_hj[["Cliente","Assessor Relacionamento","Net Em M"]],how="left",on="Cliente")

    tabela_aviso.drop ("Assessor Relacionamento_y",axis=1,inplace=True)

    tabela_aviso.rename (columns={"Assessor Relacionamento_x":"Assessor Relacionamento"},inplace=True)

    tabela_aviso.sort_values (by="Net Em M",ascending=False,inplace=True)

    # Juntando Tabela Aviso com clientes_rodrigo para descobrir o Assessor Indicador

    assessor_indicador.rename (columns={"Conta":"Cliente"},inplace=True)

    tabela_aviso = pd.merge (tabela_aviso,assessor_indicador[["Assessor Indicador","Cliente"]],how="left",on="Cliente")

    tabela_aviso["Assessor Indicador"].fillna (tabela_aviso["Assessor Relacionamento"],axis=0,inplace=True)

    tabela_aviso ["Assessor Indicador"] = tabela_aviso ["Assessor Indicador"].apply (lambda x: x.replace ("A",""))

    tabela_aviso = tabela_aviso [["Nome assessor","Assessor Relacionamento","Cliente","NomeCliente","EmailCliente","Net Em M","Assessor Indicador","Data de Aniversário","Data Aviso: 10 Dias de Antecedência"]]

    # Tabela Aniversariantes

    dia_de_hoje = date.today ().strftime ("%Y-%m-%d")

    tabela_aniversariantes = tabela_completa.loc [tabela_completa["Data de Aniversário"]==dia_de_hoje,:]
        
    tabela_aniversariantes.drop ("Data Aviso: 10 Dias de Antecedência",axis=1,inplace=True)

    tabela_aniversariantes = pd.merge (tabela_aniversariantes,clientes_rodrigo,how="left",on="Cliente")

    tabela_aniversariantes ["Assessor Relacionamento"].fillna (tabela_aniversariantes["Assessor"],inplace=True)

    tabela_aniversariantes ["Assessor Relacionamento"] = tabela_aniversariantes ["Assessor Relacionamento"].astype (str) 

    tabela_aniversariantes.loc [tabela_aniversariantes["Assessor Relacionamento"]!="Atendimento Fatorial","Assessor Relacionamento"] = tabela_aniversariantes.loc [tabela_aniversariantes["Assessor Relacionamento"]!="Atendimento Fatorial","Assessor Relacionamento"].apply (lambda x: x.replace ("A",""))

    tabela_aniversariantes = pd.merge (tabela_aniversariantes,assessores_leal,how="left",left_on="Assessor Relacionamento",right_on="Código assessor")

    tabela_aniversariantes.drop (["Código assessor","Time"],axis=1,inplace=True)

    tabela_aniversariantes ["Nome assessor"].fillna (tabela_aniversariantes["Assessor Relacionamento"],inplace=True)

    tabela_aniversariantes.drop ("Assessor",axis=1,inplace=True)

    tabela_aniversariantes = pd.merge (tabela_aniversariantes,captacao_hj[["Cliente","Net Em M"]],how="left",on="Cliente")

    tabela_aniversariantes.sort_values (by="Net Em M",ascending=False,inplace=True)

    tabela_aniversariantes = pd.merge (tabela_aniversariantes,assessor_indicador[["Cliente","Assessor Indicador"]],how="left",on="Cliente")

    tabela_aniversariantes ["Assessor Indicador"].fillna (tabela_aniversariantes["Assessor Relacionamento"],axis=0,inplace=True)

    tabela_aniversariantes ["Assessor Indicador"] = tabela_aniversariantes ["Assessor Indicador"].apply (lambda x: x.replace ("A",""))

    tabela_aniversariantes = tabela_aniversariantes [["Nome assessor","Assessor Relacionamento","Cliente","NomeCliente","EmailCliente","Net Em M","Assessor Indicador","Data de Aniversário"]]


    # Colocando nome do indicador na tabela aviso

    assessores_leal.rename (columns={"Código assessor":"Assessor Indicador"},inplace=True)

    assessores_leal.rename (columns={"Nome assessor":"Nome assessor Indicador"},inplace=True)

    assessores_leal ["Assessor Indicador"] = assessores_leal ["Assessor Indicador"].astype (str)

    tabela_aviso ["Assessor Indicador"] = tabela_aviso ["Assessor Indicador"].astype (str)

    tabela_aviso = pd.merge (tabela_aviso,assessores_leal[["Assessor Indicador","Nome assessor Indicador"]],how="left",on="Assessor Indicador")

    tabela_aviso ["Nome assessor Indicador"].fillna (tabela_aviso["Assessor Indicador"],inplace=True)

    tabela_aviso = tabela_aviso [["Nome assessor","Assessor Relacionamento","Cliente","NomeCliente","EmailCliente","Net Em M","Assessor Indicador","Nome assessor Indicador","Data de Aniversário","Data Aviso: 10 Dias de Antecedência"]]

    tabela_aviso.rename (columns={"Nome assessor":"Nome assessor Relacionamento"},inplace=True)

    # Colocando nome do indicador na tabela aniversariantes

    tabela_aniversariantes ["Assessor Indicador"] = tabela_aniversariantes ["Assessor Indicador"].astype (str)

    tabela_aniversariantes = pd.merge (tabela_aniversariantes,assessores_leal[["Assessor Indicador","Nome assessor Indicador"]],how="left",on="Assessor Indicador")

    tabela_aniversariantes.rename (columns={"Nome assessor":"Nome assessor Relacionamento"},inplace=True)

    tabela_aniversariantes ["Nome assessor Indicador"].fillna (tabela_aniversariantes["Assessor Indicador"],inplace=True)


    tabela_aniversariantes = tabela_aniversariantes [["Nome assessor Relacionamento","Assessor Relacionamento","Cliente","NomeCliente","EmailCliente","Net Em M","Assessor Indicador","Nome assessor Indicador","Data de Aniversário"]]

    # coloca o assessor indicador na tabela completa

    assessor_indicador.rename (columns={"Cliente":"Conta"},inplace=True)
    tabela_completa = tabela_completa.merge(assessor_indicador[['Conta', 'Assessor Indicador']], how='left', left_on='Cliente', right_on='Conta')
    tabela_completa['Assessor Indicador'] = tabela_completa['Assessor Indicador'].astype(str)
    del tabela_completa['Conta']

    # ajusta as colunas das tabelas de aviso e aniversariantes

    buffer = io.BytesIO()
    
    tabela_aviso.drop('EmailCliente', axis=1, inplace=True)
    tabela_aviso.drop('Net Em M', axis=1, inplace=True)
    tabela_aniversariantes.drop('EmailCliente', axis=1, inplace=True)
    tabela_aniversariantes.drop('Net Em M', axis=1, inplace=True)


    writer = pd.ExcelWriter(buffer, engine='xlsxwriter', datetime_format = 'dd/mm/yyyy')
    tabela_completa.to_excel(writer , sheet_name='Tabela_Completa',index=False)
    tabela_aviso.to_excel(writer , sheet_name='Tabela_Aviso10D',index=False)
    tabela_aniversariantes.to_excel(writer , sheet_name='Tabela_Hoje',index=False)

    #Definir as tabelas na planilha através de um loop

    lista_tabelas = [
    (tabela_completa, 'Tabela_Completa', 'Table Style Medium 2'), 
    (tabela_aviso, 'Tabela_Aviso10D', 'Table Style Medium 2'), 
    (tabela_aniversariantes, 'Tabela_Hoje', 'Table Style Medium 2')
    ]

    for tabela, nome_aba, estilo in lista_tabelas:

        arquivo = writer.book
        aba = writer.sheets[nome_aba]
        
        colunas = [{'header':column} for column in tabela.columns ]
        (lin, col) = tabela.shape

        aba.add_table(0 , 0 , lin , col-1 , {
            'columns': colunas,
            'style': estilo, 
            'autofilter': False
            })      
    
    writer.save ()

    dbx.files_upload(
        f = buffer.getvalue(), 
        path = f'/Fatorial/Inteligência/Codigos/aniversario_diario/tabela_aniversariantes.xlsx', 
        mode=dropbox.files.WriteMode.overwrite)

    st.write("\nRelatório de Aniversário Salvo no Dropbox.")

    st.download_button(
        'Baixar o Relatório', 
        buffer,
        file_name = f'tabela_aniversariantes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    if enviar_email == True:

        return None

        def open_outlook():
            try:
                subprocess.call(['C:\Program Files\Microsoft Office\Office15\Outlook.exe'])
                os.system("C:\Program Files\Microsoft Office\Office15\Outlook.exe")
            except:
                print("Outlook didn't open successfully")

        # atualiza o arquivo que tem só a tabela
        gera_excel(tabela_completa, caminho_tabela)

        # envio do email com o arquivo criado para a Lara

        informations = [['Renata Schneider', 'renata.schneider@fatorialinvest.com.br']]
        assessor = informations[0][0]
        email_destino= informations[0][1]

        # criar a integração com o outlook
        outlook = win32.Dispatch('outlook.application')
        mapi = outlook.GetNameSpace('MAPI')

        # criar um email
        email = outlook.CreateItem(0)
        email.To = email_destino
        email._oleobj_.Invoke(*(64209,0,8,0,mapi.Accounts.Item('3613leo@gmail.com')))
        email.Subject = "Aniversários Fatorial"

        # adiciona assinatura
        file_path = str(caminho_tabela.absolute())
        email.Attachments.Add(file_path)

        # corpo do email
        body = f"""
        <p>Olá, {assessor}<p>

        <p>Aqui é o Leonardo Motta, da Inteligência da Fatorial.<p>

        <p>Segue em anexo o documento que compila todos os aniversários de clientes 
        da fatorial, atualizado hoje.<p>

        <p>Qualquer dúvida estou à disposição.<p>

        <p><p>Att,<p>
        <p>Leonardo Gonçalves Motta<p>
        """

        # configurar as informações do seu e-mail
        email.HTMLBody = body
        
        email.display()
        email.Send()
        print(f"\nEmail Enviado para {assessor}\n")

def ranking_diario(data_hoje):

    # Base de Dados

    captacao_acumulado = Get.captacao_total()

    captacao_acumulado = captacao_acumulado.groupby('Código assessor').sum()[['Captação Líquida']].reset_index(drop=False)

    captacao_acumulado.rename(columns={'Captação Líquida' : 'Acumulado 2022'}, inplace=True)

    captacao_acumulado = captacao_acumulado.astype({'Código assessor':str})

    captacao_hj = Get.captacao(data_hoje)

    captacao_hj = captacao_hj.merge(captacao_acumulado, how='left', on='Código assessor')

    captacao_hj = captacao_hj [["Time","Nome assessor","Captação Líquida", "Acumulado 2022"]]

    captacao_hj['Acumulado 2022'] += captacao_hj['Captação Líquida']

    captacao_hj = captacao_hj.loc [captacao_hj["Time"]!="Fora da Fatorial",:]

    captacao_hj = captacao_hj.loc [captacao_hj["Time"]!="Total Fatorial",:]

    captacao_hj = captacao_hj.sort_values  (by="Captação Líquida",ascending=False)

    captacao_hj = captacao_hj [["Nome assessor","Time","Captação Líquida", "Acumulado 2022"]]

    # Diretório do Excel
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Paulo Valinote"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Paulo Barros"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Paulo Monfort"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Base Fatorial"].index)

    buffer = io.BytesIO()

    writer = pd.ExcelWriter(buffer, 
                            engine='xlsxwriter', 
                            datetime_format = 'dd/mm/yyyy')

    captacao_hj.to_excel(writer , sheet_name= 'Geral' , index= False)

    aba = writer.sheets['Geral']
        
    colunas = [{'header':column} for column in captacao_hj.columns ]
    (lin, col) = captacao_hj.shape

    aba.add_table(0 , 0 , lin , col-1 , {
        'columns': colunas,
        'style': 'Table Style Medium 2', 
        'autofilter': False
        })

    # Ranking filtrado

    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Time'] == "Digital"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Time'] == "Mesa RV"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Time'] == "Não Comercial"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Time'] == "Saiu da Fatorial"].index)

    '''captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Beatriz Paiva"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Flávio Camargo"].index)
    captacao_hj = captacao_hj.drop(captacao_hj[captacao_hj['Nome assessor'] == "Renata Schneider"].index)'''

    socios = ('Rodrigo Cabral', 'Jansen Costa', 'Octavio Bastos', 'Pablo Langenbach')
    captacao_hj = captacao_hj[~captacao_hj['Nome assessor'].isin(socios)]

    captacao_hj["Pipeline"] = ''
    captacao_hj = captacao_hj [["Nome assessor","Time","Captação Líquida", "Acumulado 2022"]]

    captacao_hj.to_excel(writer , sheet_name= 'Filtrado' , index= False)

    aba = writer.sheets['Filtrado']
        
    colunas = [{'header':column} for column in captacao_hj.columns ]
    (lin, col) = captacao_hj.shape

    aba.add_table(0 , 0 , lin , col-1 , {
        'columns': colunas,
        'style': 'Table Style Medium 2', 
        'autofilter': False
        })

    writer.save()

    year = Data(data_hoje).year

    dbx.files_upload(
        f = buffer.getvalue(), 
        path = f'/Fatorial/Inteligência/Codigos/ranking_diario/arquivos/{year}/ranking_{data_hoje}.xlsx', 
        mode=dropbox.files.WriteMode.overwrite)

    st.write("Ranking de Captação Salvo no Dropbox.")

    st.download_button(
        'Baixar o Relatório', 
        buffer,
        file_name = f'ranking_{data_hoje}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def rotina_coe(dia_hoje):

    mes = Data(dia_hoje).text_month

    COE_dataset = Get.coe_diario(mes)

    clientes_rodrigo = Get.clientes_rodrigo()

    assessores = Get.assessores()

    positivador = Get.positivador(dia_hoje)

    df_obj = Dataframe(COE_dataset)

    df_obj.add_assessor_relacionamento(clientes_rodrigo, column_assessor=None, positivador=positivador)

    df_obj.add_nome_assessor(assessores, 'Assessor Relacionamento')

    df_obj.reorder_columns('Assessor Relacionamento', 0)

    df_obj.reorder_columns('Nome assessor', 1)

    COE_dataset = df_obj.dataframe

    COE_dataset['Financeiro'] = COE_dataset['Financeiro'].str[3:]
    COE_dataset['Financeiro'] = COE_dataset['Financeiro'].str.replace(',', '')
    COE_dataset['Financeiro'] = COE_dataset['Financeiro'].str.replace('.', '')
    COE_dataset['Financeiro'] = COE_dataset['Financeiro'].astype(float)/100

    COE_dataset['Comissão'].replace('---', 0, inplace=True)

    COE_dataset['Comissão assessor'] = COE_dataset['Financeiro']*COE_dataset['Comissão']

    obj = Dataframe(COE_dataset)

    obj.reorder_columns('Comissão assessor', 6)

    COE_dataset = obj.dataframe

    assessores_geraram = COE_dataset['Assessor Relacionamento'].drop_duplicates()

    gerou_COE = assessores['Código assessor'].isin(assessores_geraram)

    controle_COE = assessores[~gerou_COE]

    comercial = controle_COE['Time'] != 'Não Comercial'

    controle_COE = controle_COE[comercial]

    controle_COE['Controle COE'] = 'Não gerou'

    buffer = io.BytesIO()

    writer = pd.ExcelWriter(buffer, engine='xlsxwriter', datetime_format = 'dd/mm/yyyy')

    COE_dataset.to_excel(writer , sheet_name= 'Registro COE' , index= False)

    controle_COE.to_excel(writer, sheet_name= 'Controle COE', index = False)

    writer.save()

    dbx.files_upload(
        f = buffer.getvalue(), 
        path = f'/Fatorial/Inteligência/Codigos/COE/Análise de COE/Relatórios/Relatório_COE_{mes}.xlsx', 
        mode=dropbox.files.WriteMode.overwrite)

    st.write('Relatório de COE disponível no Dropbox')

    st.download_button(
        'Baixar o Relatório', 
        buffer,
        file_name = f'Relatório_COE_{mes}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@st.cache(ttl=60*30, max_entries=50)
def get_most_recent_data(input_date=date.today(), return_type='cod'):
    '''return type msut be either "cod" or "datetime".'''

    counter = 0

    while True:
        try:
            data_hoje = get_cod_data(input_date - timedelta(days=counter))
            posi = Get.positivador(data_hoje)
            break
        except ApiError:
            counter +=1
    if return_type == 'cod': 
        return data_hoje
    elif return_type == 'datetime':
        return date(
            year = 2000 + int(data_hoje[4::]),
            month = int(data_hoje[2:4:]),
            day=int(data_hoje[:2:])
        )

def get_filtered_posi(name, data_hoje, assessores):
        
    if name == ['Atendimento Fatorial']: 
        celula = 'digital'
        
    elif name == ['Exclusive']: 
        celula =  'exclusive'

    elif name == ['Private']: 
        celula =  'private'

    mes = Data(data_hoje).text_month

    positivador = Get.positivador(data_hoje)

    suitability = Get.suitability()
    clientes_rodrigo = Get.clientes_rodrigo()

    if name[0] in ['Atendimento Fatorial', 'Exclusive']:

        base = Get.base_b2c(mes, celula)

        cols = ['Cliente', 'Responsável']
        base = base[cols]

    cod_cels = {
        'digital':'26839',
        'exclusive':'26994',
        'private':'26877'
    }
    
    if name != ['Fatorial']:
        cod_filtrados = assessores.loc[assessores['Nome assessor'].isin(name), 'Código assessor'].to_list()
        positivador = positivador[positivador['Assessor'].isin(cod_filtrados)]

    positivador_obj = Dataframe(positivador)
    
    positivador_obj.add_assessor_indicador(clientes_rodrigo)

    positivador = positivador_obj.dataframe

    suitability = suitability[['CodigoBolsa', 'NomeCliente', 'Telefone', 'Celular', 'EmailCliente']]

    df = suitability.merge(positivador, how='right', left_on='CodigoBolsa', right_on='Cliente')

    del df['CodigoBolsa']

    if name[0] in ['Atendimento Fatorial', 'Exclusive']:

        df = df.merge(base, how='left', on='Cliente')

    df_obj = Dataframe(df)
    
    df_obj.add_nome_assessor(assessores, 'Assessor Indicador')
    
    df = df_obj.dataframe

    df.rename(columns={'Nome assessor': 'Indicador'}, inplace=True)

    df = Dataframe(df)

    df.add_nome_assessor(assessores, 'Assessor')

    df = df.dataframe

    df.rename(columns={'Nome assessor': 'Relacionamento'}, inplace=True)


    if name[0] in ['Atendimento Fatorial', 'Exclusive']:
        

        df  = df[['Indicador', 'Relacionamento', 'Responsável', 'Cliente', 'NomeCliente', 'Profissão', 
            'Telefone', 'Celular', 'EmailCliente', 'Sexo', 'Segmento', 'Data de Cadastro',
            'Fez Segundo Aporte?', 'Data de Nascimento',
            'Status', 'Ativou em M?', 'Evadiu em M?', 'Operou Bolsa?',
            'Operou Fundo?', 'Operou Renda Fixa?', 'Aplicação Financeira Declarada',
            'Receita no Mês', 'Receita Bovespa', 'Receita Futuros',
            'Receita RF Bancários', 'Receita RF Privados', 'Receita RF Públicos',
            'Captação Bruta em M', 'Resgate em M', 'Captação Líquida em M',
            'Captação TED', 'Captação ST', 'Captação OTA', 'Captação RF',
            'Captação TD', 'Captação PREV', 'Net em M-1', 'Net Em M',
            'Net Renda Fixa', 'Net Fundos Imobiliários', 'Net Renda Variável',
            'Net Fundos', 'Net Financeiro', 'Net Previdência', 'Net Outros',
            'Receita Aluguel', 'Receita Complemento/Pacote Corretagem']]
    else:
        df  = df[['Indicador', 'Relacionamento', 'Cliente', 'NomeCliente', 'Profissão', 
            'Telefone', 'Celular', 'EmailCliente', 'Sexo', 'Segmento', 'Data de Cadastro',
            'Fez Segundo Aporte?', 'Data de Nascimento',
            'Status', 'Ativou em M?', 'Evadiu em M?', 'Operou Bolsa?',
            'Operou Fundo?', 'Operou Renda Fixa?', 'Aplicação Financeira Declarada',
            'Receita no Mês', 'Receita Bovespa', 'Receita Futuros',
            'Receita RF Bancários', 'Receita RF Privados', 'Receita RF Públicos',
            'Captação Bruta em M', 'Resgate em M', 'Captação Líquida em M',
            'Captação TED', 'Captação ST', 'Captação OTA', 'Captação RF',
            'Captação TD', 'Captação PREV', 'Net em M-1', 'Net Em M',
            'Net Renda Fixa', 'Net Fundos Imobiliários', 'Net Renda Variável',
            'Net Fundos', 'Net Financeiro', 'Net Previdência', 'Net Outros',
            'Receita Aluguel', 'Receita Complemento/Pacote Corretagem']]

    return df

def get_filtered_diversificador(name, data_hoje, assessores):

    if name[0] in ['Atendimento Fatorial', 'Exclusive']:

        if name == ['Atendimento Fatorial']: 
            celula = 'digital'
            
        elif name == ['Exclusive']: 
            celula =  'exclusive'

        mes = Data(data_hoje).text_month
    
        diversificador = Get.diversificador(data_hoje)

        suitability = Get.suitability()
        clientes_rodrigo = Get.clientes_rodrigo()

        base = Get.base_b2c(mes, celula)

        cols = ['Cliente', 'Responsável']
        base = base[cols]

        cod_cels = {
            'digital':'26839',
            'exclusive':'26994'
        }

        diversificador = diversificador[diversificador['Assessor'] == cod_cels[str.lower(celula)]]

        diversificador_obj = Dataframe(diversificador)
        
        diversificador_obj.add_assessor_indicador(clientes_rodrigo)

        diversificador = diversificador_obj.dataframe

        suitability = suitability[['CodigoBolsa', 'NomeCliente', 'Telefone', 'Celular', 'EmailCliente']]

        df = suitability.merge(diversificador, how='right', left_on='CodigoBolsa', right_on='Cliente')

        del df['CodigoBolsa']

        df = df.merge(base, how='left', on='Cliente')

        df_obj = Dataframe(df)
        
        df_obj.add_nome_assessor(assessores, 'Assessor Indicador')
        
        df = df_obj.dataframe

        df.rename(columns={'Nome assessor': 'Indicador'}, inplace=True)

        obj_df = Dataframe(df)

        obj_df.reorder_columns('Indicador',0)

        obj_df.reorder_columns('Responsável',1)

        del obj_df.dataframe['Assessor Indicador']

        return obj_df.dataframe

    else:
        diversificador = Get.diversificador(data_hoje)

        cod_assessor = assessores.loc[ assessores['Nome assessor'] == name[0], 'Código assessor'].iloc[0]

        diversificador = diversificador[ diversificador['Assessor'] == cod_assessor ]

        return diversificador

def display_relatorio_info(title, data_hoje, explanation, input_list = None):

    data_obj = Data(data_hoje)
    st.write(f'### {title}')

    col1, space, col2 = st.columns([2,0.15,1])

    col2.write("##### Sobre o relatório")
    
    col2.markdown(explanation, unsafe_allow_html=True)

    if input_list == None:
        selected_data = col1.date_input(f'Selecione a data do {title}: ', date(day= (data_obj.day), month= (data_obj.month), year= (data_obj.year + 2000)))
    else:
        selected_data = col1.multiselect(f'Selecione os filtros do relatório: ', input_list)
    
    col1.markdown(f'''<div style="text-align: justify;"> <font size="2"> 
    O dado mais recente é do dia <b>{data_obj.day}/{data_obj.month}/{data_obj.year} </b>
    </font> </div>''', unsafe_allow_html=True)

    espacamento(1, col1)

    botao_capt = col1.button(f'Gerar {title}')

    espacamento(2, st)

    return botao_capt, selected_data

def get_captacao_por_cliente(data_hoje, name, assessores):

    posi = Get.captacao(data_hoje, sheet_name='Positivador M')
    transf = Get.captacao(data_hoje, sheet_name='Transferêcnias')
    perdidos = Get.captacao(data_hoje, sheet_name='Perdidos')
    suitability = Get.suitability()

    if name != ['Fatorial']:

        cod_assessor = assessores.loc[ assessores['Nome assessor'] == name[0], 'Código assessor'].iloc[0]

        posi = posi[ (posi['Assessor correto'] == cod_assessor) & (posi['Captação Líquida em M'] != 0) ]
        transf = transf[ (transf['Assessor correto'] == cod_assessor) & (transf['Net em M-1'] != 0) ]
        perdidos = perdidos[ (perdidos['Assessor correto'] == cod_assessor) & (perdidos['Net Em M'] != 0) ]

    cols = ['Assessor', 'Cliente', 'Captação', 'Natureza']

    posi = posi[['Assessor correto', 'Cliente', 'Captação Líquida em M']]
    transf = transf[['Assessor correto', 'Cliente', 'Net em M-1']]
    perdidos = perdidos[['Assessor correto', 'Cliente', 'Net Em M']]

    perdidos['Net Em M'] *= -1

    posi['Natureza'] = 'Externa'
    transf['Natureza'] = 'Interna'
    perdidos['Natureza'] = 'Interna'

    posi.columns = cols
    transf.columns = cols
    perdidos.columns = cols

    df = Dataframe(pd.concat([posi, transf, perdidos]))

    df.add_nome_cliente(suitability)

    df.reorder_columns('NomeCliente', 2)

    return df.dataframe

def filter_receita(input_filter, receitas):

    list_df = []

    for relatorio in input_filter:

        if relatorio == 'Apenas assessores':
            
            df = receitas.groupby('Nome assessor').sum()[['Receita']]
        
        elif relatorio == 'Apenas verticais':
            df = receitas.groupby('Centro de Custo').sum()[['Receita']]
        
        elif relatorio == 'Assessores por Vertical':
            df = receitas.groupby(['Nome assessor', 'Centro de Custo']).sum()[['Receita']]
        
        elif relatorio == 'Assessores por mês':
            df = receitas.groupby(['Nome assessor', 'Data Completa']).sum()[['Receita']]

        elif relatorio == 'Verticais por mês':
            df = receitas.groupby(['Centro de Custo', 'Data Completa']).sum()[['Receita']]

        elif relatorio == 'Assessores por vertical por mês':
            df = receitas.copy()
    
        df.reset_index(inplace=True)

        list_df += [df]
    return list_df

def filter_captacao(input_filter, captacao):

    if input_filter[0] == 'Apenas assessores':
        
        df = captacao.groupby('Nome assessor').sum()
    
    elif input_filter[0] == 'Assessores por mês':
        df = captacao.groupby(['Nome assessor', 'Mes']).sum()
    
    df.reset_index(inplace=True)

    df = df[['Nome assessor', 'Total conta velha', 'Total conta nova', 'Total transferências', 'Total contas perdidas', 'Captação Líquida']]
    
    return df

def filter_nps(year, assessores):

    envios, ranking_assessores, ranking_onboarding = Get.nps_anual(year=year)

    ranking_assessores.rename(columns={'Nº de registros' : 'Respostas NPS'}, inplace=True)
    ranking_onboarding.rename(columns={'Nº de registros' : 'Respostas Onboarding'}, inplace=True)

    envios = envios.loc[envios['Survey status'] != 'NOT STAMPLED', ['Código Assessor', 'Survey status']]

    envios = envios.groupby('Código Assessor').count()

    df = ranking_assessores.merge(ranking_onboarding, how='outer', on='Assessor')

    df = df.merge(envios, how='left', left_on='Assessor', right_on='Código Assessor')

    df['XP - Relacionamento - Aniversário - NPS Assessor'].fillna(df['XP - Relacionamento - Onboarding - NPS'])

    df[['Respostas NPS', 'Respostas Onboarding']] = df[['Respostas NPS', 'Respostas Onboarding']].fillna(0)

    df['Respostas NPS'] = df['Respostas NPS'].astype(float) + df['Respostas Onboarding'].astype(float)

    df = df[['Assessor', 'Respostas NPS', 'Survey status', 'XP - Relacionamento - Aniversário - NPS Assessor']]

    df.columns = ['Código assessor', 'Respostas NPS', 'Envios NPS', 'Nota NPS']

    df['% Respostas'] = df['Respostas NPS'].astype(float) / df['Envios NPS'].astype(float)

    df['Código assessor'] = df['Código assessor'].str.lstrip('A')

    df = df.merge(assessores[['Código assessor', 'Nome assessor']], how='left', on='Código assessor')

    df = Dataframe(df)
    
    df.reorder_columns('Nome assessor', 1)

    return df.dataframe

def confere_bases_b2b(data_hoje, A_digital = '26839', A_exclusive = '26994'):

    positivador = Get.positivador(data_hoje)
    suitability = Get.suitability()
    suitability = suitability[['CodigoBolsa', 'NomeCliente']]

    mes = Data(data_hoje).text_month
    
    ## importando os dados

    base_digital = Get.base_b2c(mes=mes, celula='digital')
    base_exclusive = Get.base_b2c(mes=mes, celula='exclusive')

    #tratamento dos dados

    mask_nao_zerado = positivador['Net Em M'] >= 1e3
    mask_ativo = positivador['Status'] == 'ATIVO'
    positivador = positivador[mask_nao_zerado & mask_ativo]

    cols = ['Assessor', 'Cliente', 'Responsável']
    base_digital = base_digital[cols]
    base_exclusive = base_exclusive[cols]

    # execução do código
    
    mask_digital = positivador['Assessor'] == A_digital
    mask_exclusive = positivador['Assessor'] == A_exclusive

    positivador_digital = positivador[mask_digital]
    positivador_exclusive = positivador[mask_exclusive]

    mask_in_digital = positivador_digital['Cliente'].isin(base_digital['Cliente'])
    mask_in_exclusive = positivador_exclusive['Cliente'].isin(base_exclusive['Cliente'])

    nao_listados_digital = positivador_digital['Cliente'][~mask_in_digital]
    nao_listados_exclusive = positivador_exclusive['Cliente'][~mask_in_exclusive]

    nao_listados_digital = pd.DataFrame(nao_listados_digital.reset_index(drop=True))
    nao_listados_exclusive = pd.DataFrame(nao_listados_exclusive.reset_index(drop=True))

    nao_listados_digital = nao_listados_digital.merge(suitability, how='left', left_on='Cliente', right_on='CodigoBolsa')
    nao_listados_exclusive = nao_listados_exclusive.merge(suitability, how='left', left_on='Cliente', right_on='CodigoBolsa')

    del nao_listados_digital['CodigoBolsa']
    del nao_listados_exclusive['CodigoBolsa']

    return nao_listados_exclusive, nao_listados_digital

def send_mail(mail_from='inteligencia.fatorial@gmail.com', mail_to=None, cc=None, subject=None, body=None, attachment=None, file_name='nome_padrao.xlsx' , mensagem='', server = 'smtp.gmail.com', port = 587):

    if type(mail_to) == list:
        mail_to = ';'.join(mail_to)
    
    senha = st.secrets['emailPassword']
    
    msg = MIMEMultipart()
    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Subject'] = subject
    message = body
    msg.attach(MIMEText(message, _subtype='html'))
    
    if attachment != None:

        if type(attachment) != list:
            attachment = [attachment]

        for buffer in attachment:
            attachment = MIMEApplication(buffer.getvalue())
            attachment['Content-Disposition'] = f'attachment; filename={file_name}'
            msg.attach(attachment)

    server = smtplib.SMTP(server, port)
    server.starttls()
    server.ehlo()
    server.login(mail_from, senha)

    server.sendmail(mail_from, mail_to, msg.as_string(),)

    server.quit()

def envia_avisos_clientes_b2b(data_hoje,
    emails_exclusive = ['rodrigo.cabral@fatorialinvest.com.br', 'moises.rodrigues@fatorialinvest.com.br', 'soraya.brum@fatorialinvest.com.br', 'alex.marinho@fatorialinvest.com.br'],
    emails_digital = ['soraya.brum@fatorialinvest.com.br', 'alex.marinho@fatorialinvest.com.br', 'rodrigo.cabral@fatorialinvest.com.br', 'moises.rodrigues@fatorialinvest.com.br', 'bruna.krivochein@fatorialinvest.com.br'],
    adress_mail = 'inteligencia.fatorial@gmail.com'):

    nao_listados_exclusive, nao_listados_digital = confere_bases_b2b(data_hoje)

    ## clientes do digital

    total_clientes_digital = len(nao_listados_digital)

    if total_clientes_digital != 0:

        html_df = nao_listados_digital.to_html(index=False, justify = 'center')

        # corpo do email
        body = f"""
        <p>Olá, Time Digital<p>
        
        <p>Aqui é o Leonardo Motta, da Inteligência da Fatorial.<p>

        <p>Fizemos um levantamento e, de acordo com a última base de separação de contas, os seguintes clientes estão sem responsável designado:<p>

        <p>{html_df}<p>

        <p><p>Att,<p>
        <p> Leonardo Gonçalves Motta <p>
        """

    else:
        body = f"""
        <p>Olá, Time Digital<p>
        
        <p>Aqui é o Leonardo Motta, da Inteligência da Fatorial.<p>

        <p>Fizemos um levantamento e, de acordo com a última base de separação de contas, não há clientes sem responsável designado.<p>

        <p><p>Att,<p>
        <p> Leonardo Gonçalves Motta <p>
        """

    send_mail(
        mail_from=adress_mail, 
        mail_to=emails_digital,
        #mail_to=['leonardo.motta@fatorialadvisors.com.br', '3613leo@gmail.com'],
        subject="[Inteligência Fatorial] Atualização da Base de Clientes Digital",
        body=body,
        mensagem='\n\nE-mail enviado para o Digital.'
    )

    ## clientes do exclusive

    total_clientes_exclusive = len(nao_listados_exclusive)

    if total_clientes_exclusive != 0:

        html_df = nao_listados_exclusive.to_html(index=False, justify = 'center')

        # corpo do email
        body = f"""
        <p>Olá, Time Exclusive<p>
        
        <p>Aqui é o Leonardo Motta, da Inteligência da Fatorial.<p>

        <p>Fizemos um levantamento e, de acordo com a última base de separação de contas, os seguintes clientes estão sem responsável designado:<p>

        <p>{html_df}<p>

        <p><p>Att,<p>
        <p> Leonardo Gonçalves Motta <p>
        """

    else:
        body = f"""
        <p>Olá, Time Exclusive<p>
        
        <p>Aqui é o Leonardo Motta, da Inteligência da Fatorial.<p>

        <p>Fizemos um levantamento e, de acordo com a última base de separação de contas, não há clientes sem responsável designado.<p>

        <p><p>Att,<p>
        <p> Leonardo Gonçalves Motta <p>
        """

    send_mail(
        mail_from=adress_mail,
        mail_to=emails_exclusive,
        #mail_to=['leonardo.motta@fatorialadvisors.com.br', '3613leo@gmail.com'],
        subject="[Inteligência Fatorial] Atualização da Base de Clientes Exclusive",
        body=body,
        mensagem='\n\nE-mail enviado para o Exclusive.'
    )   

def envia_captacao(data_hoje, mail_to, assessores, adress_mail = 'inteligencia.fatorial@gmail.com'):

    obj_data = Data(data_hoje)
    dia, mes, ano = obj_data.day, obj_data.month, obj_data.year

    captacao = Get.captacao(data_hoje)

    posi_exclusive = get_filtered_posi(['Exclusive'], data_hoje, assessores)

    posi_digital = get_filtered_posi(['Atendimento Fatorial'], data_hoje, assessores)

    resumo = captacao[['Código assessor', 'Nome assessor', 'Time', 'Qtd Clientes XP', 'NET XP']]

    def get_resumo_carteira_b2c(posi):
        resumo_net = posi[['Responsável', 'Net Em M']].groupby('Responsável').sum()
        resumo_clients = posi[['Responsável', 'Cliente']].groupby('Responsável').count()
        resumo = resumo_clients.merge(resumo_net, how='left', right_index=True, left_index=True)
        resumo.rename(columns={'Net Em M': 'NET XP', 'Cliente': 'Qtd. Cliente XP'}, inplace=True)
        return resumo

    resumo_digital = get_resumo_carteira_b2c(posi_digital)
    resumo_excluisive = get_resumo_carteira_b2c(posi_exclusive)

    buffer = io.BytesIO()

    writer = pd.ExcelWriter(buffer , engine='xlsxwriter', datetime_format = 'dd/mm/yyyy')
    resumo.to_excel(writer, sheet_name='Resumo')
    resumo_digital.to_excel(writer, sheet_name='Resumo Digital')
    resumo_excluisive.to_excel(writer, sheet_name='Resumo Exclusive')
    writer.save()

    def format_html(resumo, index=False):
        html_df = resumo.copy()
        if 'Código assessor' in html_df.columns:
            html_df.drop('Código assessor', axis=1, inplace=True)
        html_df.sort_values(by='NET XP', ascending = False, inplace=True)
        html_df['NET XP'] = html_df['NET XP'].apply(lambda x: 'R$ {:,.2f}'.format(x))
        html_df = html_df.to_html(justify='center', index=index)
        return html_df

    html_df = format_html(resumo)
    html_df_digital = format_html(resumo_digital, index=True)
    html_df_exclusive = format_html(resumo_excluisive, index=True)

    body = f'''
    <p>
    Olá, Cabral! Tudo bem?
    </p>

    <p>
    Segue abaixo um resumo com as carteiras de cada assessor.
    </p>
    
    <p> <b> Toda Fatorial </b> </p>
    {html_df}

    <p>
    Aqui segue as distribuições do digital e do exclusive:
    </p>

    <p> <b> Digital </b> </p>
    {html_df_digital}
    <p> <b> Exclusive </b> </p>
    {html_df_exclusive}

    <p>
    Att,
    </p>

    <img src="https://i.ibb.co/qMt33Ny/Assinatura-Analista-Leonardo.jpg" alt="Assinatura-Analista-Leonardo" border="0">
    '''

    send_mail(
        mail_from=adress_mail,
        mail_to= mail_to,
        subject=f'Resumo das carteiras em {dia}/{mes}/{ano}',
        body=body,
        attachment=buffer,
        file_name=f'resumo_carteiras_{data_hoje}.xlsx',
        mensagem='Resumo de Carteiras Enviado.'
        )
    
    return buffer

def filtra_clientes_rodrigo(clientes_rodrigo):

    clientes_char, clientes_thieme = Get.clientes_antigos()

    clientes_rodrigo['Conta'] = clientes_rodrigo['Conta'].astype(str)

    clientes_char['Cliente'] = clientes_char['Cliente'].astype(str)
    clientes_thieme['Cliente'] = clientes_thieme['Cliente'].astype(str)

    mask_char = clientes_rodrigo['Conta'].isin(clientes_char['Cliente'])
    mask_thieme = clientes_rodrigo['Conta'].isin(clientes_thieme['Cliente'])

    clientes_rodrigo.loc[mask_char, 'Assessor Relacionamento'] = 'Era do Char'
    clientes_rodrigo.loc[mask_thieme, 'Assessor Relacionamento'] = 'Era da Thieme'

    return clientes_rodrigo

def horizontal_singular_bar(data, index=[''], reference=st):

    with st.container():

        df = pd.DataFrame(data, index= index)

        fig = px.bar(data, width=800, height=210, orientation='h',
        color_discrete_sequence=['#1D2843','#99a7c8'])

        fig.update_yaxes(showticklabels=False)

        fig.update_traces(marker_line_color='rgb(8,48,107)',
                        marker_line_width=0.1, opacity=.96, width = .5)

        reference.plotly_chart(fig, use_container_width=True)

        fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0, pad=0), 
        paper_bgcolor='#EFE5DC',
        plot_bgcolor = '#EFE5DC'
        )

def remove_header_space():
    st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

class NPS:

    def get_dataset(list_atendimento = ['bruna.krivochein@fatorialinvest.com.br'], list_exclusive = ['soraya.brum@fatorialinvest.com.br', 'alex.marinho@fatorialinvest.com.br', 'brenno.alo@fatorialinvest.com.br'], list_private = ['renata.schneider@fatorialinvest.com.br', 'yago.meireles@fatorialinvest.com.br']):
        
        pesquisas = Get.pesquisas_nps()
        prev = Get.prev_nps()
        ranking = Get.ranking_nps()
        respostas = Get.respostas_nps()


        suitability = Get.suitability()

        respostas['Assessor'] = respostas['Assessor'].astype(str)
        pesquisas['Assessor'] = pesquisas['Assessor'].astype(str)
        prev['Assessor'] = prev['Assessor'].astype(str)
        ranking['Assessor'] = ranking['Assessor'].astype(str)

        respostas['Código Cliente'] = respostas['Código Cliente'].astype(str)
        pesquisas['Cliente'] = pesquisas['Cliente'].astype(str)
        prev['Código Cliente'] = prev['Código Cliente'].astype(str)

        assessores = Get.assessores()
        mails = Get.emails()
        mails = mails[['Código assessor', 'Email']]

        assessores = assessores.merge(mails, how='left', on='Código assessor')

        assessores['Email'].fillna('3613leo@gmail.com', inplace=True)

        pesquisas = pesquisas[['Cliente', 'Data de Envio', 'Pesquisa Relacionamento', 'Status', 'O e-mail foi aberto?', 'Pelo App?', 'Assessor']]

        pesquisas = Dataframe(pesquisas)
        pesquisas.add_nome_cliente(suitability, 'Cliente')
        pesquisas.reorder_columns('NomeCliente', position=3)
        pesquisas = pesquisas.dataframe

        assessores.loc[assessores['Código assessor'] == '26839', 'Email'] = ";".join(list_atendimento)
        assessores.loc[assessores['Código assessor'] == '26994', 'Email'] = ";".join(list_exclusive)
        assessores.loc[assessores['Código assessor'] == '26877', 'Email'] = ";".join(list_private)

        del assessores['Time']

        return assessores, pesquisas, prev, ranking, respostas

    def get_body(nome, list_tables):

        body =  f'''
        <p>
        Oii, {nome}! Tudo bem?
        </p>
        
        <p>
        Segue abaixo informações sobre NPS dos últimos 30 dias, que serão úteis para novas captações e retenção de clientes. 
        </p>
        '''

        for header, table, index in list_tables:
            body += f'''
            <p> <b> {header} </b> </p>
            <p> {table.to_html(justify='center', index=index)} </p>'''

        body += f'''
        <p>
        Qualquer dúvida, à disposição.
        </p>

        <p>
        Atenciosamente,
        </p>

        <img src="https://i.imgur.com/4mUfaot.png" alt="Assinatura Louise Miranda - Fatorial Investimentos" border="0">'''

        return body

    def format_date(dataframe, data_column):
        
        data_string = []
        for i in dataframe.index:
            data_string.append(dataframe.loc[i, data_column].strftime('%d/%m/%Y'))
        dataframe[data_column] = data_string

        return dataframe
        

    def play_routine(mail_qualidade =  'inteligencia@fatorialinvest.com.br'):

        assessores, pesquisas, prev, ranking, respostas = NPS.get_dataset()

        for assessor, nome, mail_to in assessores.to_numpy():

            first_name = nome.split(' ')[0]

            # ranking

            ranking_assessor = ranking.loc[ ranking['Assessor'] == assessor, ['NPS', 'Percentual de Respostas', 'Assessor']]
            del ranking_assessor['Assessor']

            if len(ranking_assessor.index) == 0:
                pass

            else:
                ranking_assessor['Percentual de Respostas'] = ranking_assessor['Percentual de Respostas'].apply(lambda x: '{:,.1f} %'.format(x*100))
                ranking_assessor = ranking_assessor.transpose()

                ranking_assessor.loc['NPS', 'Objetivo'] = 95
                ranking_assessor.loc['Percentual de Respostas', 'Objetivo'] = '40,0%'
                
                ranking_assessor.columns = ['Assessor', 'Objetivo']
                ranking_assessor.index = ['Nota NPS', '% Respostas']

            # pesquisa

            pesquisas_assessor = pesquisas.loc[ pesquisas['Assessor'] == assessor, :]
            del pesquisas_assessor['Assessor']
            pesquisas_assessor = NPS.format_date(pesquisas_assessor, 'Data de Envio')
        
            # prev

            prev_assessor = prev.loc[ prev['Assessor']== assessor, :]
            del prev_assessor['Assessor']
            prev_assessor = NPS.format_date(prev_assessor, 'Data de Resposta')

            # envios
            
            respostas_assessor = respostas.loc[ respostas['Assessor'] == assessor, :]
            del respostas_assessor['Assessor']
            respostas_assessor = NPS.format_date(respostas_assessor, 'Data de Resposta')

            list_tables = [] # array element: [Title, Dataframe, Useful Index]

            if len(ranking_assessor.index) > 0: list_tables.append(['Resumo', ranking_assessor, True])
            if len(pesquisas_assessor.index) > 0: list_tables.append(['Pesquisas pendentes', pesquisas_assessor, False])
            if len(prev_assessor.index) > 0: list_tables.append(['Interesse em Previdência', prev_assessor, False])
            if len(respostas_assessor.index) > 0: list_tables.append(['Pesquisas Respondidas', respostas_assessor, False])

            if len(list_tables) > 0:
                
                body = NPS.get_body(first_name, list_tables)

                subject = f'Dashboard NPS - {nome} {date.today().strftime("%d/%m")}'

                send_mail(mail_from=mail_qualidade, mail_to=mail_to, subject=subject, body=body, mensagem=f'Email enviado para {nome}')

    def relatorios():
        # exporta as bases de dados

        suitability = Get.suitability()

        clientes_rodrigo = Get.clientes_rodrigo()

        list_files = st.file_uploader("Upload dos arquivos: ", accept_multiple_files=True, )

        if list_files is not None:

            for i in range(180):
                sleep(1)
                if len(list_files) == 7:
                    break

            if len(list_files) == 7:

                st.write('Iniciou o relatorio')

                ranking_assessores, nps_onboarding, pesquisas, pesquisas_app, indicacoes, respostas, prev = list_files

                ranking_assessores = pd.read_excel(ranking_assessores, skiprows=4)
                del ranking_assessores['Classificação']

                nps_onboarding = pd.read_excel(nps_onboarding, skiprows=4)
                del nps_onboarding['Classificação']

                pesquisas = pd.read_excel(pesquisas, skiprows=2)

                pesquisas_app = pd.read_excel(pesquisas_app, skiprows=2)

                indicacoes = pd.read_excel(indicacoes, skiprows=2)

                respostas = pd.read_excel(respostas, skiprows=2)
                respostas['Customer ID'] = respostas['Customer ID'].astype(str)

                prev = pd.read_excel(prev, skiprows=2)
                prev['Customer ID'] = prev['Customer ID'].astype(str)

                caminho_excel = r'/Fatorial/Inteligência/Codigos/NPS/Relatórios/Relatório Ranking NPS.xlsx'
                caminho_indicacoes = r'/Fatorial/Inteligência/Codigos/NPS/Relatórios/Relatório Indicações.xlsx'
                caminho_pesquisas= r'/Fatorial/Inteligência/Codigos/NPS/Relatórios/Relatório Pesquisas.xlsx'
                caminho_respostas = r'/Fatorial/Inteligência/Codigos/NPS/Relatórios/Relatório Respostas.xlsx'
                caminho_prev = r'/Fatorial/Inteligência/Codigos/NPS/Relatórios/Relatório Prev.xlsx'

                # COL NAMES

                ranking_assessores.rename(columns={'Nº de registros': 'Tamanho da amostra'}, inplace=True)
                nps_onboarding.rename(columns={'Nº de registros': 'Tamanho da amostra'}, inplace=True)

                # PASSANDO OS CLIENTES DO MOISES PARA O ATENDIMENTO

                ranking_assessores['Assessor'].replace('A68959', 'A26839', inplace=True)

                mask_atendimento = ranking_assessores['Assessor'] == 'A26839'

                n_respostas_atendimento = ranking_assessores.loc[mask_atendimento, 'Tamanho da amostra']
                nota_atendimento = ranking_assessores.loc[mask_atendimento, 'XP - Relacionamento - Aniversário - NPS Assessor']

                media = 0
                for i, nota in enumerate(nota_atendimento):
                    n_resp = n_respostas_atendimento.to_numpy()[i]
                    media += nota*n_resp

                n_respostas_atendimento = n_respostas_atendimento.sum()
                nota_atendimento = media/n_respostas_atendimento

                ranking_assessores = ranking_assessores[~mask_atendimento]
                ranking_assessores = ranking_assessores.append({
                    'Assessor': 'A26839', 
                    'Tamanho da amostra': n_respostas_atendimento, 
                    'XP - Relacionamento - Aniversário - NPS Assessor': nota_atendimento
                    }, 
                    ignore_index=True)

                nps_onboarding['Assessor'].replace('A68959', 'A26839', inplace=True)
                pesquisas['Código Assessor'].replace('A68959', 'A26839', inplace=True)
                indicacoes['Assessor'].replace('A68959', 'A26839', inplace=True)

                # filtragem básica das indicações

                indicacoes.columns = ['Data de resposta', 'Cliente', 'Assessor', 'Recomendaria?', 'Indicação', 'Contato', 'E-mail']
                indicacoes.dropna(subset=['Indicação'], inplace=True)
                indicacoes['Assessor'] = indicacoes['Assessor'].str.lstrip('A')


                # une as bases considerando a nota do NPS geral, só preenchendo as notas dos assessores sem presença no geral com as notas do onboarding, e somando os volumes de resposta

                ranking_assessores = ranking_assessores.merge(nps_onboarding, how='outer', on='Assessor')

                ranking_assessores['Tamanho da amostra_x'].fillna(0, inplace=True)
                ranking_assessores['Tamanho da amostra_y'].fillna(0, inplace=True)

                ranking_assessores['Tamanho da amostra'] = ranking_assessores['Tamanho da amostra_x'] + ranking_assessores['Tamanho da amostra_y']

                ranking_assessores['NPS'] = ranking_assessores['XP - Relacionamento - Aniversário - NPS Assessor'].fillna(ranking_assessores['XP - Relacionamento - Onboarding - NPS'])

                del ranking_assessores['XP - Relacionamento - Aniversário - NPS Assessor']
                del ranking_assessores['XP - Relacionamento - Onboarding - NPS']
                del ranking_assessores['Tamanho da amostra_x']
                del ranking_assessores['Tamanho da amostra_y']

                # filtar o envio de pesquisas

                envio_de_pesquisas = pesquisas[['Código Assessor', 'Customer ID', 'Survey status']]

                mask_not_sampled = envio_de_pesquisas['Survey status'] == 'NOT_SAMPLED'

                envio_de_pesquisas = envio_de_pesquisas[~mask_not_sampled]

                envio_de_pesquisas = envio_de_pesquisas.groupby('Código Assessor').count()

                envio_de_pesquisas.rename(columns={'Survey status': 'Volume de Envios'}, inplace=True)

                # junta o ranking e os envios das respostas para obter o volume de pesquisas enviadas

                ranking_assessores = pd.merge(ranking_assessores, envio_de_pesquisas, how='outer', left_on='Assessor', right_index=True)

                ranking_assessores.fillna(0, inplace=True)

                ranking_assessores['Percentual de Respostas'] = ranking_assessores['Tamanho da amostra']/ranking_assessores['Volume de Envios']

                ranking_assessores.sort_values(['NPS', 'Percentual de Respostas'], inplace=True, ascending=False)

                ranking_assessores.reset_index(drop=True, inplace=True)

                index = [i + 1 for i in ranking_assessores.index]

                ranking_assessores.index = index

                ranking_assessores = Dataframe(ranking_assessores)

                ranking_assessores.reorder_columns(ranking_assessores, col_name='NPS', position=1)

                ranking_assessores = ranking_assessores.dataframe

                ranking_assessores['Assessor'] = ranking_assessores['Assessor'].str.lstrip('A')
                ranking_assessores['Percentual de Respostas'] = ranking_assessores['Percentual de Respostas'].replace(inf, 0)

                #filtragem básica do envio de pesquisas

                pesquisas.columns = ['ID', 'Pesquisa Relacionamento', 'Data de Criação', 'Data de Resposta', 'Data de Envio', 'Cliente', 'Assessor', 'Escritório', 'Status', 'A pesquisa foi clicada?', 'O e-mail foi aberto?', 'Segmento', 'Data de cadastro', 'Null1', 'Null']
                pesquisas['Assessor'] = pesquisas['Assessor'].str.lstrip('A')
                pesquisas['Status'] = pesquisas['Status'].replace({'DELIVERED': 'Enviada', 'DELIVERED_AND_REMINDED':'Enviada e alertada'})
                mask_not_aplicable = pesquisas['Status'].isin(['COMPLETED', 'NOT_SAMPLED'])
                pesquisas = pesquisas[~mask_not_aplicable]
                pesquisas.dropna(subset=['Data de Envio'], inplace=True)

                pesquisas = Dataframe(pesquisas)

                pesquisas.add_assessor_relacionamento(pesquisas, clientes_rodrigo)

                pesquisas = pesquisas.dataframe
                del pesquisas['Assessor']
                pesquisas.rename(columns={'Assessor Relacionamento': 'Assessor'}, inplace=True)
                pesquisas['Assessor'] = pesquisas['Assessor'].str.replace("Atendimento Fatorial", '26839')
                pesquisas.drop_duplicates('Cliente', inplace=True)

                pesquisas_app = pesquisas_app['Survey ID']

                mask_pesquisas_app = pesquisas['ID'].isin(pesquisas_app)

                pesquisas.loc[mask_pesquisas_app, 'Pelo App?'] = 'Sim'

                pesquisas['Pelo App?'].fillna("Não", inplace=True)

                indicacoes = Dataframe(indicacoes)

                indicacoes.add_assessor_relacionamento(indicacoes, clientes_rodrigo)

                indicacoes = indicacoes.dataframe
                del indicacoes['Assessor']
                indicacoes.rename(columns={'Assessor Relacionamento': 'Assessor'}, inplace=True)
                indicacoes['Assessor'] = indicacoes['Assessor'].str.replace("Atendimento Fatorial", '26839')

                ranking_assessores['Assessor'] = ranking_assessores['Assessor'].str.replace("Atendimento Fatorial", '26839')

                mask_maior_100 = ranking_assessores['Percentual de Respostas'] > 1
                ranking_assessores.loc[mask_maior_100, 'Percentual de Respostas'] = 1

                ranking_assessores.drop_duplicates(subset='Assessor', inplace=True)

                # respostas

                respostas = respostas[[
                    'Código Assessor',
                    'Customer ID', 
                    'Responsedate',
                    'Pesquisa Relacionamento', 
                    'XP - Relacionamento - Aniversário - NPS Assessor', 
                    'XP - Relacionamento - Onboarding - NPS', 
                    'XP - Relacionamento - Aniversário - Comentário NPS Assessor', 
                    'XP - Relacionamento - Aniversário - Recomendaria Assessor',
                    'XP - Relacionamento - Aniversário - Email amigo/familiar'
                    ]]

                respostas['XP - Relacionamento - Aniversário - NPS Assessor'].fillna(respostas['XP - Relacionamento - Onboarding - NPS'], inplace=True)

                del respostas['XP - Relacionamento - Onboarding - NPS']

                respostas.columns = [
                    'Assessor',
                    'Código Cliente', 
                    'Data de Resposta',
                    'Pesquisa Relacionamento', 
                    'NPS', 
                    'Comentário NPS Assessor', 
                    'Indicaria o assessor?',
                    'Contato indicado'
                    ]

                respostas.fillna(' ', inplace=True)

                respostas = Dataframe(respostas)

                respostas.add_nome_cliente(respostas, 'Código Cliente', suitability = suitability)
                respostas.reorder_columns(respostas, 'NomeCliente', 2)

                respostas = respostas.dataframe

                respostas['Assessor'] = respostas['Assessor'].str.lstrip('A')

                # prev

                prev = prev[['Responsedate','Customer ID','Assessor','Ask Now Question #1','Ask Now Question #2']]

                prev['Assessor'] = prev['Assessor'].str.lstrip('A')

                prev.columns = [
                    'Data de Resposta',
                    'Código Cliente',
                    'Assessor',
                    'Onde está a previdência?',
                    'Cliente quer receber comparativo ou proposta de prev?'
                ]

                prev = Dataframe(prev)

                prev.add_nome_cliente(prev, 'Código Cliente', suitability)
                prev.reorder_columns(prev, 'NomeCliente', 2)

                prev = prev.dataframe

                # gera excel

                buffer = to_excel(ranking_assessores, index=True)
                dbx.files_upload(
                f = buffer.getvalue(), 
                path = caminho_excel, 
                mode=dropbox.files.WriteMode.overwrite)

                buffer = to_excel(indicacoes, index=True)
                dbx.files_upload(
                f = buffer.getvalue(), 
                path = caminho_indicacoes, 
                mode=dropbox.files.WriteMode.overwrite)

                buffer = to_excel(pesquisas, index=True)
                dbx.files_upload(
                f = buffer.getvalue(), 
                path = caminho_excel, 
                mode=dropbox.files.WriteMode.overwrite)

                buffer = to_excel(prev, index=True)
                dbx.files_upload(
                f = buffer.getvalue(), 
                path = caminho_prev, 
                mode=dropbox.files.WriteMode.overwrite)

class ResumoCarteira:
    @st.cache(ttl=60*30, max_entries=50, allow_output_mutation=True)
    def get_resumo(posi, assessores, suitability, clientes_rodrigo, nomes_filtrados):

        capt_clientes = Get.captacao_cliente()
        receita_clientes = Get.receitas_cliente()

        ## filtra capt_clientes pelos últimos 12 meses e último mês

        capt_clientes.sort_values('Data Completa', inplace=True, ascending=False)
        period = capt_clientes['Data Completa'].drop_duplicates()

        month = get_meses()

        dict_month = pd.DataFrame( [[ month[i] , j, datetime.datetime(2000 + j, i+1, 1).strftime("%Y - %m")] for i in range(12) for j in [22,23,24]] , columns = ['Mes', 'Ano', 'Month'])

        # 12 meses

        capt_clientes_12 = capt_clientes.loc[ capt_clientes['Data Completa'].isin(period.head(12)) ]
        capt_clientes_12 = capt_clientes_12.groupby('Cliente').sum()[['Captação Líquida em M']].reset_index(drop=False)
        capt_clientes_12.columns = ['Cliente', 'Captação 12 meses']

        #captacao mes

        capt_mes = capt_clientes.loc[capt_clientes['Cliente'].isin(posi['Cliente'])]
        capt_mes = capt_mes.groupby(['Mes', 'Ano']).sum()[['Captação Líquida em M']].reset_index()
        capt_mes = capt_mes.merge(dict_month, how='left', on=['Mes', 'Ano'])
        capt_mes.sort_values(by='Month', inplace=True)

        # M-1

        capt_clientes_1 = capt_clientes.loc[ capt_clientes['Data Completa'].isin(period.head(1)) ]
        mes_capt = capt_clientes_1['Mes'].iloc[0]
        ano_capt = capt_clientes_1['Ano'].iloc[0]
        capt_clientes_1 = capt_clientes_1[['Cliente', 'Captação Líquida em M']]
        capt_clientes_1.columns = ['Cliente', f'Captação {mes_capt} {ano_capt}']

        ## filtra receitas_clientes pelos últimos 12 meses e último mês

        receita_clientes.sort_values('Data Completa', inplace=True, ascending=False)
        period = receita_clientes['Data Completa'].drop_duplicates()

        # 12 meses

        receita_clientes_12 = receita_clientes.loc[ receita_clientes['Data Completa'].isin(period.head(12)) ]
        receita_clientes_12 = receita_clientes_12.groupby('Cliente').sum()[['Valor Bruto Recebido']].reset_index(drop=False)
        receita_clientes_12.columns = ['Cliente', 'Receitas 12 meses']

        # receita mes
        receitas_mes = receita_clientes.loc[receita_clientes['Cliente'].isin(posi['Cliente'])]
        receitas_mes = receitas_mes.groupby(['Mes', 'Ano']).sum()[['Valor Bruto Recebido']].reset_index()
        receitas_mes = receitas_mes.merge(dict_month, how='left', on=['Mes', 'Ano'])
        receitas_mes.sort_values(by='Month', inplace=True)

        # M-1

        receita_clientes_1 = receita_clientes.loc[ receita_clientes['Data Completa'].isin(period.head(1)) ]
        mes_receita = receita_clientes_1['Mes'].iloc[0]
        ano_receita = receita_clientes_1['Ano'].iloc[0]
        receita_clientes_1 = receita_clientes_1.groupby('Cliente').sum()[['Valor Bruto Recebido']].reset_index(drop=False)
        receita_clientes_1.columns = ['Cliente', f'Receita {mes_receita} {ano_receita}']

        # inicia a organização do df

        df = posi[['Cliente', 'Status', 'Net Em M']]

        how= 'left'

        df = df.merge(capt_clientes_1 , how=how, on ='Cliente')
        df = df.merge(capt_clientes_12, how=how, on ='Cliente')

        df['Status'].fillna('Saiu da Fatorial', inplace=True)

        df = df.merge(receita_clientes_1, how=how, on='Cliente')
        df = df.merge(receita_clientes_12, how=how, on='Cliente')

        df['Status'].fillna('Fora da XP', inplace=True)

        df = df.merge(receita_clientes[['Cliente', 'Category']].drop_duplicates(), how='left', on='Cliente')

        df['ROA 12 meses'] = df['Receitas 12 meses']/df['Net Em M']
        df[f'ROA {mes_receita} {ano_receita}'] = df[f'Receita {mes_receita} {ano_receita}']/df['Net Em M'] * 12

        df = Dataframe(df)

        df.add_assessor_relacionamento(clientes_rodrigo, column_conta = 'Cliente', positivador = posi, column_assessor=None)
        df.add_nome_assessor(assessores, 'Assessor Relacionamento')
        df.add_nome_cliente(suitability)

        df = df.dataframe

        df = df[[
            'Assessor Relacionamento',
            'Nome assessor',
            'Cliente',
            'NomeCliente',
            'Category',
            'Status',
            f'Captação {mes_capt} {ano_capt}',
            'Captação 12 meses',
            'Net Em M',
            f'Receita {mes_receita} {ano_receita}',
            'Receitas 12 meses',
            f'ROA {mes_receita} {ano_receita}',
            'ROA 12 meses'
        ]]

        df['NomeCliente'].fillna(df['Cliente'], inplace=True)

        df['ROA 12 meses'].fillna(0, inplace=True)
        df[f'ROA {mes_receita} {ano_receita}'].fillna(0, inplace=True)

        df['ROA 12 meses'].replace(np.inf,0, inplace=True)
        df[f'ROA {mes_receita} {ano_receita}'].replace(np.inf, 0, inplace=True)

        return df, capt_mes, receitas_mes

def get_last_month(data_hoje):

    month = int(data_hoje[2:4])
    year = int(data_hoje[4:])

    months = get_meses()

    if month == 1:
        last_month = 12
        last_year = year - 1
    
    else:
        last_month = month-1
        last_year = year
    
    cod_day = '01'
    if month > 9:
        cod_month = str(last_month)
    else:
        cod_month = '0' + str(last_month)
    cod_year = str(year)

    return cod_day + cod_month + cod_year
   
def get_most_recent_data_receita(receitas):

    periodos = receitas[['Mes', 'Ano', 'Data Completa']].drop_duplicates()

    periodos = periodos.sort_values(by=['Data Completa'], ascending=False)

    mes = periodos['Mes'].head(1).iloc[0]
    ano = periodos['Ano'].head(1).iloc[0]

    return mes, ano