from functions import st, timedelta

from config import list_functions, most_recent_data, assessores
from functions import NPS, Data
from functions import envia_captacao, envia_avisos_clientes_b2b, get_most_recent_data, get_last_fechamento, aniversario, get_cod_data, captacao, export_files_captacao, ranking_diario, rotina_coe
import text_data

def app(name, most_recent_data=most_recent_data, assessores=assessores):

    # header

    st.write("""
    # Rotinas Inteligência
    """)

    rotina = st.selectbox('Selecione a Rotina:', list_functions)

    if rotina == 'Captação':

        st.write("""
        ### Captação Diário
        """)

        st.markdown(text_data.rotina_captacao_explanation, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)
            cod_data_ontem = get_most_recent_data(data_hoje - timedelta(days=1))
            cod_data_mes_passado = get_last_fechamento(cod_data_hoje)

            posi_novo, posi_d1, posi_velho, clientes_rodrigo, assessores, lista_transf, clientes_novos_ontem, suitability = export_files_captacao(cod_data_hoje, cod_data_ontem, cod_data_mes_passado)

            captacao(posi_novo, posi_velho, clientes_rodrigo, assessores, lista_transf, clientes_novos_ontem, suitability, cod_data_hoje)

    elif rotina == 'Aniversário':
        st.write("""
        ### Aniversário Diário
        """)

        st.markdown(text_data.rotina_aniversario_explanation, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)

            cod_data_ontem = get_most_recent_data(data_hoje - timedelta(days=1))

            aniversario(cod_data_hoje, cod_data_ontem)

    elif rotina == 'Ranking Diário':
        st.write("""
        ### Ranking de Captação
        """)

        st.markdown(text_data.rotina_ranking_explanation, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)

            ranking_diario(cod_data_hoje)
    
    elif rotina == 'COE':
        st.write("""
        ### Rotina de COE
        """)

        st.markdown(text_data.rotina_COE_explanation, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)

            rotina_coe(cod_data_hoje)
    
    elif rotina == 'Avisos Bases B2C':
        st.write("""
        ### Envio de avisos B2C
        """)

        st.markdown(text_data.rotina_aviso_bases_B2C_explanation, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)

            envia_avisos_clientes_b2b(cod_data_hoje)

            st.write('E-mails enviados para Digital e Exclusive')

    elif rotina == 'Resumo Carteiras':
        st.write("""
        ### Resumo de Carteiras
        """)

        st.markdown(text_data.rotina_aviso_bases_relatorio_carteira, unsafe_allow_html=True)

        most_recent_data = Data(most_recent_data).datetime

        data_hoje = st.date_input('Data do último positivador: ', most_recent_data)

        dar_inicio = st.button('Gerar Relatório')

        if dar_inicio:

            cod_data_hoje = get_most_recent_data(data_hoje)

            mail_to = ['rodrigo.cabral@fatorialinvest.com.br', 'obastos@fatorialinvest.com.br', 'pablo.langenbach@fatorialinvest.com.br', 'jansen@fatorialinvest.com.br', 'marcio.murad@fatorialadvisors.com.br']

            df = envia_captacao(cod_data_hoje, mail_to, assessores)

            st.write('Resumo de Carteiras Enviado')

            st.download_button(
                label='Baixar o Relatório',
                data=df,
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    elif rotina == 'Relatório NPS':
        st.write("""
        ### Relatório NPS
        """)

        st.markdown(text_data.rotina_NPS, unsafe_allow_html=True)

        run = st.button('Iniciar NPS')

        if run:
            NPS.relatorios()



