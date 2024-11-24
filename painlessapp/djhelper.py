# Helper functions to user throughout the app.
from .models import Folder, PassKey
from django.contrib.auth.models import User
import secrets
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.core.cache import cache


# TO-DO:
# Add randomized encryption key function, then extend instantiate user to include the function
# as a means to encrypting the PassKey.enc_key value prior to storage. The default, for now, has "unenc-"
# pre-pended to it for testing to know between the unencrypted and encrypted variants.
def create_gen_enc_key():
    gen_enc_key = "unenc-" + secrets.token_urlsafe(120)
    return gen_enc_key


# Takes user's salt and creates an instance of Fernet used to decrypt or encrypt later
# Used for user's GEK only
def create_fernet_key(salt, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt, encoding="utf-8"),
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(bytes(password, encoding="utf-8")))
    return Fernet(key)


# Takes input of (Fernet, token) to encrypt the token.
def encrypt_gen_enc_key(fernetkey, token):
    enc_token = fernetkey.encrypt(bytes(token, encoding="utf-8"))
    return enc_token.decode("utf-8")


# Takes input of (Fernet, token) to decrypt the token.
def decrypt_gen_enc_key(fernetkey, token):
    dec_token = fernetkey.decrypt(bytes(token, encoding="utf-8"))
    return dec_token.decode("utf-8")


# Encrypts user passwords before storing it in their password storage
def encrypt_user_pass(userid, new_pass):
    # Grab user FKEY and GEK for encryption
    user_FKEY = cache.get(str(userid) + "-FKEY")
    user_GEK = cache.get(str(userid) + "-GEK")

    # Check if FKEY is available to use to encrypt the user's password. If not, make it from GEK:
    if user_FKEY is None:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes("None", encoding="utf-8"),
            iterations=480000,
        )
        user_FKEY = base64.urlsafe_b64encode(kdf.derive(bytes(str(user_GEK), encoding="utf-8")))
        cache.set(str(userid) + "-FKEY", user_FKEY, None)

    enc_NewPass = Fernet(user_FKEY).encrypt(bytes(new_pass, encoding="utf-8"))

    # Decode the encrypted password
    return enc_NewPass.decode("utf-8")


# Decrypts user passwords before showing it in their password storage
def decrypt_user_pass(userid, enc_pass):
    # Grab user FKEY and GEK for encryption
    user_FKEY = cache.get(str(userid) + "-FKEY")
    user_GEK = cache.get(str(userid) + "-GEK")

    # Check if FKEY is available to use to decrypt the user's password. If not, make it from GEK:
    if user_FKEY is None:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes("None", encoding="utf-8"),
            iterations=480000,
        )
        user_FKEY = base64.urlsafe_b64encode(kdf.derive(bytes(str(user_GEK), encoding="utf-8")))
        cache.set(str(userid) + "-FKEY", user_FKEY, None)

    dec_pass = Fernet(user_FKEY).decrypt(bytes(enc_pass, encoding="utf-8"))

    # Decode the encrypted password
    return dec_pass.decode("utf-8")


# Takes user and password then returns the decrypted GEK
def decrypt_and_store_key(userid, userpass):
    # Initialize pass_key object to pull encryption details
    user_pass_key = PassKey.objects.get(user_id=userid)
    user_key = create_fernet_key(user_pass_key.salt, userpass)
    user_encrypted_key = user_pass_key.enc_key
    unenc_user_gek = decrypt_gen_enc_key(user_key, user_encrypted_key)
    cache.set(str(userid) + "-GEK", unenc_user_gek, None)


# This creates the user and then also initiates default objects which require foreign key references.
# For example, user "jim" is created and a default folder model "None" is created.
# Eventually, if I get this far, this should house special encryption functions
# that assigns the user an encryption key which will be used to encrypt user passwords.
# The encryption key ideally would be encrypted by the user and stored encrypted, so only
# the user would be able to decrypt it to view their data. That's a long-shot goal, though.
def instantiate_user(username, password, email=None):
    # Enforce email set to None.
    # TODO: May be redundant. Maybe delete from definition?
    email = None

    # Create new user
    new_user = User.objects.create_user(username, email, password)

    # Create encryption key
    salt = base64.b64encode(os.urandom(16)).decode("utf-8")
    fernet_key = create_fernet_key(salt, password)
    gen_enc_key = create_gen_enc_key()
    enc_token = encrypt_gen_enc_key(fernet_key, gen_enc_key)
    # Store user's encryption key and salt
    PassKey.objects.create(user_id=new_user, salt=salt, enc_key=enc_token)

    # Create default folder
    Folder.objects.create(name="No Folder", user_id=new_user)
    return new_user
