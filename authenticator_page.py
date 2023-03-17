from imports import random, pickle, stauth, Path


from config import assessores

def app():

    names = assessores['Nome assessor'].drop_duplicates().to_list()
    
    usernames = assessores['Código assessor'].drop_duplicates().astype(str).to_list()

    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)

    authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "key1", str(random()), cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login("Login", "main")
    
    return name, authentication_status, username, authenticator
