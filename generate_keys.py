from imports import pickle, stauth, Path

from functions import Get

assessores = Get.assessores()

names = assessores['Nome assessor'].to_list()
usernames = assessores['Código assessor'].to_list()
passwords = (assessores['Nome assessor'].str.replace(' ', '').str.lower() + ',123').to_list()

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)