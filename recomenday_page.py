from imports import st, mysql, pd, datetime, px
from functions import to_excel

def app(username):

    conn = mysql.connector.connect(host="database-fatorial.cna0vemrrmju.us-east-2.rds.amazonaws.com",user="admin", password="Fatorial,123", database="FatorialInvestimentos")

    cur = conn.cursor()

    st.write('''
    # Recomenday
    ''')

    col1, space, col2 = st.columns([1, .2, 2])

    registro = False
    manage_crm = True

    if registro == True:

        lead_indicado = col1.text_input('Nome Completo')

        telefone = col1.text_input('Telefone/Whatsapp')

        cliente = col1.text_input('Código do Cliente que Indicou')

        relacionamento = col1.selectbox('Relacionamento do cliente com o indicado', ['Trabalho', 'Colégio', 'Esporte', 'Faculdade', 'Família', 'Outros'])

        enviar = col1.button('Registrar')

        if enviar:

            test_lead_indicado = lead_indicado != ""
            test_telefone = telefone != ""
            test_relacionamento = relacionamento != []

            cur.execute('''
                SELECT DISTINCT codigo_cliente FROM dados_clientes c;
                '''
                )
            myresult = cur.fetchall()

            df = pd.DataFrame(myresult, columns=['Cliente'])

            test_cliente = cliente in df['Cliente'].to_list()

            if test_lead_indicado and test_relacionamento and test_telefone:

                if test_cliente:

                    try:
                        cur.execute(f'''
                            INSERT INTO indicacoes_recomenday
                            VALUES(%s,%s,%s,%s,%s,%s);
                        ''', [username,lead_indicado,telefone,cliente,relacionamento,datetime.datetime.now()]                    
                        )
                        conn.commit()

                        col1.success('Preenchido com sucesso!')

                    except:

                        col1.error('Esse lead já foi registrado!')

                else:
                    st.warning('ATENÇÃO: Selecione um Código de Cliente Existente.')
            
            else:
                st.warning('ATENÇÃO: Preencha todos os campos.')

        cur.execute('''
            SELECT * FROM indicacoes_recomenday
            WHERE codigo_assessor = %s''', [username])
        
        myresult = cur.fetchall()

        df = pd.DataFrame(myresult, columns=['Assessor','Indicação','Telefone','Cliente','Relacionamento','Data'])

        col1.write('''
            ### Deletar um Registro
        ''')

        indicacao_errada = col1.selectbox('Assessor', df['Indicação'])

        delete = col1.button('Deletar Registro')

        if delete:
            cur.execute('''DELETE FROM indicacoes_recomenday
            WHERE nome_indicado = %s''', [indicacao_errada])

            conn.commit()

            col1.success('Lead Deletado com Sucesso')

        if username != "Inteligência":

            cur.execute('''
                SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.relacionamento FROM indicacoes_recomenday i
                JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente
                WHERE i.codigo_assessor = %s;
                ''', [username])
            
        else:
            cur.execute('''
                    SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.relacionamento FROM indicacoes_recomenday i
                    JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente;
                    ''')
        
        myresult = cur.fetchall()

        df = pd.DataFrame(myresult, columns=['Assessor','Indicação','Telefone','Cliente','Relacionamento','Data'])

        df.index += 1

    if manage_crm:

        if username != "Inteligência":

            cur.execute('''
                SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.status FROM indicacoes_recomenday i
                JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente
                WHERE i.codigo_assessor = %s;
                ''', [username])
            
        else:
            cur.execute('''
                    SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.status FROM indicacoes_recomenday i
                    JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente;
                    ''')
        
        myresult = cur.fetchall()

        df = pd.DataFrame(myresult, columns=['Assessor','Indicação','Telefone','Cliente','Nome Cliente','Status'])

        df.index += 1

        leads = col1.multiselect('Leads', df['Indicação'])

        new_status = col1.selectbox('Status', ['Indicação', 'Contato Feito', 'Reunião Marcada', 'Cliente Convertido'])

        atualizar = col1.button('Atualizar Status')

        if atualizar:
            placeholders = ', '.join(['%s'] * (len(leads) + 1))
            cur.execute('''
                UPDATE indicacoes_recomenday
                SET status = %s
                WHERE nome_indicado IN (\'''' + "','".join(leads) + '\');'
            , [new_status])

            conn.commit()

            col1.success('Status Atualizado com Sucesso')

    col2.write('#### Seus registros')

    if username != "Inteligência":

        cur.execute('''
            SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.status FROM indicacoes_recomenday i
            JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente
            WHERE i.codigo_assessor = %s;
            ''', [username])
            
    else:
        cur.execute('''
                SELECT i.codigo_Assessor, i.nome_indicado, telefone, i.codigo_cliente, c.nome_cliente, i.status FROM indicacoes_recomenday i
                JOIN dados_clientes c ON c.codigo_cliente = i.codigo_cliente;
                ''')
        
    myresult = cur.fetchall()

    df = pd.DataFrame(myresult, columns=['Assessor','Indicação','Telefone','Cliente','Nome Cliente','Status'])

    if username == 'Inteligência':
        del df['Telefone']
    else:
        del df['Assessor']

    df.index += 1
    
    col2.write(df)

    df_by_status = df.groupby('Status').count()[['Indicação']].reset_index()

    df = to_excel(df)

    col2.download_button(
        label='Exportar Indicações',
        data = df,
        file_name = f'Indicações Recomenday.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    for i, title in enumerate(['Indicação', 'Contato Feito', 'Reunião Marcada', 'Cliente Convertido']):
        df_by_status.replace(title, f'{i+1}.{title}', inplace=True)

    df_by_status.sort_values(by=['Status'], ascending=True, inplace=True)
    
    fig = px.bar(df_by_status, 'Status', 'Indicação')

    fig.update_traces(marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',)

    col1.plotly_chart(fig, use_container_width=True)
        
        

    
