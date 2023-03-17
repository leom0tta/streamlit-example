from imports import st, pd, px

pd.options.plotting.backend = "plotly"

st.set_page_config(page_title= 'Fatorial Assessores' ,page_icon = '',layout='wide')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

data = {'Captação Interna': [4], 'Captação Externa':[2]}

def _max_width_(prcnt_width:int = 75):
    max_width_str = f"max-width: {prcnt_width}%;"
    st.markdown(f""" 
                <style> 
                .reportview-container .main .block-container{{{max_width_str}}}
                </style>    
                """, 
                unsafe_allow_html=True,
    )

#_max_width_()

def horizontal_singular_bar(data, index=[''], reference=st):

    with st.container():

        df = pd.DataFrame(data, index= index)

        fig = px.bar(data, width=800, height=210, orientation='h',
        color_discrete_sequence=['#1D2843','#233154'])

        fig.update_yaxes(showticklabels=False)

        fig.update_traces(marker_line_color='rgb(8,48,107)',
                        marker_line_width=0.1, opacity=.96)

        reference.plotly_chart(fig, use_container_width=True)

        fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0, pad=0), 
        paper_bgcolor='#EFE5DC',
        plot_bgcolor = '#EFE5DC'
        )

st.write("""
    # Fatorial Site
    """)

st.sidebar.write('Test')

st.multiselect('Test', ['Test1', 'Test2'])

col1, col2 = st.columns(2)

col1.multiselect('Testing', ['Test1', 'Test2'])
col2.multiselect('Testando', ['Test1', 'Test2'])

col1, col2 = st.columns([1,3])

col1.write('')
col1.write('')
col1.write('')

col1.metric('Example: ', 10000)

horizontal_singular_bar(data, reference=col2)

df = pd.DataFrame({
    'Clientes Novos':['Bruna Da Silva', 'Bruna Da Silva', 'Bruna Da Silva', 'Bruna Da Silva'],
    'PL de Entrada':['R$ 300,000.00', 'R$ 300,000.00', 'R$ 300,000.00', 'R$ 300,000.00'],
    'Transferência?':['Sim' for i in range(4)]
    })

col1, space, col2 = st.columns([1, .4, 1.5])

col1.write('##### Header')
col1.markdown(f"{df.to_html(index=False)}", unsafe_allow_html=True)

col1.write('')

col1.write('##### Header')
col1.markdown(f"{df.to_html(index=False)}", unsafe_allow_html=True)

data = dict(
    number=[39, 27.4, 20.6, 11, 2],
    stage=["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"])

fig = px.funnel(data, x='number', y='stage')

fig.update_traces(marker_color='rgb(29,40,67)', marker_line_color='rgb(29,40,67)',
                  marker_line_width=1.5, opacity=.96)

col2.plotly_chart(fig, use_container_width=True)

positivador = pd.DataFrame({ i: 12 for i in ['Cliente', 'Captação TED', 'Captação ST', 'Captação OTA', 'Captação RF', 'Captação TD', 'Captação PREV']}, index= [i for i in range(7)])

positivador['Captação ST'] += positivador['Captação OTA']

del positivador['Captação OTA']

tipos_de_capt = positivador[['Cliente', 'Captação TED', 'Captação ST', 'Captação RF', 'Captação TD', 'Captação PREV']].sum()

tipos_de_capt = tipos_de_capt.transpose().reset_index()

tipos_de_capt.columns = ['Segmento de Captação', 'Captação']

tipos_de_capt.index = ['TED', 'STVM', 'OTA', 'Renda Fixa', 'Tesouro Direto', 'Previdência']

st.write(tipos_de_capt)

fig = px.pie(tipos_de_capt, 'Segmento de Captação', 'Captação')

st.plotly_chart(fig, use_container_width=True)


