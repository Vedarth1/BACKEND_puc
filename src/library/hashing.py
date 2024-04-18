# password_hashing.py
from src import bcrypt

def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password

def check_password_hash(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)
