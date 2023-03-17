from imports import st, tempfile

from functions import Get, stream_dropbox_file, dbx
from config import adms, private, exclusive, digital, team_jansen

def app(name):

    superranking = Get.superranking_total()

    # header

    st.write("""
    # Super Ranking
    """)

    superranking.loc[superranking['Nome assessor'].isin(['Jansen Costa', 'Octavio Bastos']), 'Time'] = 'B2C'

    complete_sr = superranking.copy()

    meses = superranking.loc[superranking['Ano'] == 23, 'Mes'].drop_duplicates().to_list()

    col1, col2 = st.columns(2)

    if name in adms:
        nomes_filtrados = col1.multiselect('Assessor', superranking['Nome assessor'].drop_duplicates().fillna(superranking['Código assessor']).sort_values())
    
    elif name in team_jansen:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Jansen Costa', 'Private'], name)

    elif name in private:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Private'])
    
    elif name in exclusive:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Exclusive', 'Atendimento Fatorial'])

    elif name in digital:
        nomes_filtrados = col1.multiselect('Assessor', [name] + ['Atendimento Fatorial'])

    else:
        nomes_filtrados = [name]

    period = col2.multiselect('Período', ['Acumulado 2023', 'Acumulado 2022'] + meses)

    if nomes_filtrados != [] and period != []:

        if not nomes_filtrados == []:
            superranking = superranking[ superranking['Nome assessor'].isin(nomes_filtrados) ]

        if period == ['Acumulado 2023']:
            year = 23
            superranking = superranking.loc[ (superranking['Ano'] == year) ]
            complete_sr = complete_sr.loc[ (complete_sr['Ano'] == year) ]
            n_meses = len(complete_sr['Mes'].drop_duplicates())
        
        elif period == ['Acumulado 2022']:
            n_meses = 4 # 4 meses de 2022
            period = ['Setembro', 'Outubro', 'Novembro', 'Dezembro']
            year = 22
            superranking = superranking.loc[ (superranking['Ano'] == year) & (superranking['Mes'].isin(period))]
            complete_sr = complete_sr.loc[ (complete_sr['Ano'] == year) & (complete_sr['Mes'].isin(period))]
        
        else:
            year = 23
            superranking = superranking.loc[ (superranking['Mes'].isin(period)) & (superranking['Ano'] == year)]
            complete_sr = complete_sr.loc[ (complete_sr['Mes'].isin(period)) & (complete_sr['Ano'] == year) ]
            n_meses = len(superranking['Mes'].drop_duplicates())
        
        complete_sr = complete_sr.groupby(['Nome assessor', 'Time']).sum()

        complete_sr[['NPS Aniversário', 'NPS Onboarding', 'Percentual de Resposta', 'Fator de Peso']] /= n_meses

        complete_sr.reset_index(drop=False, inplace=True)

        complete_sr = complete_sr[ complete_sr['Time'] == 'B2B']

        try: 

            pts_geral = complete_sr.loc[complete_sr['Nome assessor'] == nomes_filtrados[0], 'Pontuação Geral'].iloc[0]
            complete_sr.sort_values(by='Pontuação Geral', ascending=False, inplace=True)
            complete_sr.reset_index(inplace=True)
            colocacao_geral = complete_sr.loc[complete_sr['Nome assessor'] == nomes_filtrados[0]].index.to_list()[0]
            
            st.write(f'''### Você está na {colocacao_geral + 1}ª colocação geral, com {round(pts_geral,2)} pontos!
            
            ''')
        except IndexError:
            pass

        col1,col2 = st.columns(2)

        def get_position(metric, nome = nomes_filtrados[0], complete_sr = complete_sr):
            if metric == 'Percentual de Resposta': 
                pts = 'Fator de Peso'
            else:
                pts = f'Pontos {metric}'
            df = complete_sr[['Nome assessor', metric, pts]]
            df.sort_values(ascending=False, by=pts, inplace=True)
            df.reset_index(drop=True, inplace=True)
            try:
                idx = df[df['Nome assessor'] ==  nome].index.to_list()[0] + 1
            except IndexError:
                idx = None
            
            if idx == 1:
                rank = "🥇"
            elif idx == 2:
                rank = "🥈"
            elif idx == 3:
                rank = "🥉"
            elif idx == None:
                rank = ""
            else:
                rank = " - " + str(idx) + "º Lugar"

            return rank
        
        #captacao

        position = get_position('Captação Líquida')
        capt_total = superranking['Captação Líquida'].sum()
        pts_capt = superranking['Pontos Captação Líquida'].sum()
        col1.write(f"""
        #### Captação Líquida (30%) {position}
        - Captação Total: **{'R$ {:,.2f}'.format(capt_total)}**
        - Pontos Captação Líquida: {pts_capt}""")

        #receita

        position = get_position('Faturamento')
        rec_total = superranking['Faturamento'].sum()
        pts_rec = superranking['Pontos Faturamento'].sum()
        col2.write(f"""
        #### Faturamento (30%) {position}
        - Receita Total: **{'R$ {:,.2f}'.format(rec_total)}**
        - Pontos Faturamento: {pts_rec}""")

        #contas novas

        position = get_position('Contas Novas')
        cn_total = superranking['Contas Novas'].sum()
        pts_cn = superranking['Pontos Contas Novas'].sum()
        col1.write(f"""
        #### Contas Novas (30%) {position}
        - Saldo Contas Novas: **{cn_total}**
        - Pontos Contas Novas: {pts_cn}""")

        #nps aniversario

        position = get_position('NPS Aniversário')
        nps1_total = superranking['NPS Aniversário'].sum()/len(superranking['NPS Aniversário'])
        pts_nps1 = superranking['Pontos NPS Aniversário'].sum()
        col2.write(f"""
        #### NPS Aniversário (5%) {position}
        - NPS Aniversário: **{round(nps1_total,2)}**
        - Pontos NPS Aniversário: {pts_nps1}""")

        #nps onboarding

        position = get_position('NPS Onboarding')
        nps2_total = superranking['NPS Onboarding'].sum()/len(superranking['NPS Onboarding'])
        pts_nps2 = superranking['Pontos NPS Onboarding'].sum()
        col1.write(f"""
        #### NPS Onboarding (5%) {position}
        - NPS Onboarding: **{round(nps2_total,2)}**
        - Pontos NPS Onboarding: {pts_nps2}""")

        #% respostas

        position = get_position('Percentual de Resposta')
        perc_resp_total = superranking['Percentual de Resposta'].sum()/len(superranking['Percentual de Resposta'])
        peso_total = superranking['Fator de Peso'].sum()
        col2.write(f"""
        #### Percentual de Respostas (Peso) {position}
        - Percentual de Respostas: **{'{:,.2f} %'.format(perc_resp_total*100)}**
        - Fator de Peso Médio: {round(peso_total,2)}""")

        file_id = r'id:OQRfgJ5J_9AAAAAAAACQQg'

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            metadata, file_content = dbx.files_download(file_id)
            tmp_file.write(file_content.content)

        bytes_obj = stream_dropbox_file('/Fatorial/Inteligência/Codigos/G20/Relatorio/Faixas de Pontuação/Simulador SR.xlsx',dbx)
        
        st.download_button('Simulador do SR', bytes_obj, 'Simulador SR.xlsx')