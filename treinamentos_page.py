from imports import st

from functions import stream_dropbox_file, dbx

data = stream_dropbox_file("/Fatorial/Inteligência/Apresentações/Treinamentos/Painel Gestão a vista com Leonardo Motta 0603 reduzido.mp4", dbx)

st.video(data)