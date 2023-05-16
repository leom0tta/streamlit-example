from imports import pd, st

from functions import send_mail
from config import assessores

def app(name):

    st.write('''
    # Alimentação Banco de Dados
    ''')

    col1, col2 = st.columns(2)

    operation = col1.selectbox('Selecione a operação: ', ['Registrar Novo Funcionário', 'Atualizar Dados de Funcionários'])

    if operation == 'Registrar Novo Funcionário':

        st.write('### Formulário')

        col1, col2 = st.columns([0.3, 0.7])

        # input data
        nome_completo = col1.text_input('Nome Completo')
        codigo_assessor = col1.text_input('Código assessor / Operacional')
        time = col1.selectbox('Time', assessores['Time'].drop_duplicates())
        email = col1.text_input('E-mail')

        registrar = st.button('Registrar')

        if registrar:

            email_ok = ("@fatorialinvest.com.br" in email) | ("@fatorialadvisors.com.br"in email)
            
            nomes_list = nome_completo.capitalize().split()

            nome_assessor = nomes_list[0] + ' ' + nomes_list[-1]

            if codigo_assessor == None:
                codigo_assessor = nome_assessor

            if email_ok:
                
                body = f'''
                <p>O usuário {name} adicionou um novo usuário ao banco de dados. Segue abaixo as informações:</p>
                
                <ul>
                    <li>Código assessor : {codigo_assessor}</li>
                    <li>Nome assessor   : {nome_assessor}</li>
                    <li>Time            : {time}</li>
                    <li>E-mail          : {email}</li>
                </ul>'''

                subject = '[Inteligênica Fatorial] Registro de Novo Funcionário'

                send_mail(mail_to=['leonardo.motta@fatorialadvisors.com.br'], 
                          subject=subject,
                          body=body)
                
            else:
                st.error('O email deve ser @fatorialinvest.com.br ou @fatorialadvisors.com.br')

    if operation == 'Atualizar Dados de Funcionários':

        st.write('### Formulário')

        col1, col2 = st.columns([0.3, 0.7])

        selected_assessor = col1.multiselect(assessores)

        # input data
        nome_completo = col1.selectbox('Nome Completo')
        codigo_assessor = col1.text_input('Código assessor / Operacional')
        time = col1.selectbox('Time', assessores['Time'].drop_duplicates())
        email = col1.text_input('E-mail')

        registrar = st.button('Registrar')

        if registrar:

            email_ok = ("@fatorialinvest.com.br" in email) | ("@fatorialadvisors.com.br"in email)
            
            nomes_list = nome_completo.capitalize().split()

            nome_assessor = nomes_list[0] + ' ' + nomes_list[-1]

            if codigo_assessor == None:
                codigo_assessor = nome_assessor

            if email_ok:
                
                body = f'''
                <p>O usuário {name} adicionou um novo usuário ao banco de dados. Segue abaixo as informações:</p>
                
                <ul>
                    <li>Código assessor : {codigo_assessor}</li>
                    <li>Nome assessor   : {nome_assessor}</li>
                    <li>Time            : {time}</li>
                    <li>E-mail          : {email}</li>
                </ul>'''

                subject = '[Inteligênica Fatorial] Registro de Novo Funcionário'

                send_mail(mail_to=['leonardo.motta@fatorialadvisors.com.br'], 
                          subject=subject,
                          body=body)
                
            else:
                st.error('O email deve ser @fatorialinvest.com.br ou @fatorialadvisors.com.br')

            




