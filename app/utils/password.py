from bcrypt import hashpw, gensalt, checkpw

salt = gensalt()


def gen_hash_pw(password: str):
    return hashpw(password.encode('utf-8'), salt=salt)


def verify_pw(password: str, saved_pw: str):
    password = password.encode('utf-8')
    return checkpw(password, saved_pw)
