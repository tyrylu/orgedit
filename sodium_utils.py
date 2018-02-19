import base64
import io
import pysodium


def encrypt(plaintext, password):
    """Encrypts the given plaintext using libsodium secretbox, key is generated using scryptsalsa208sha256 with a random salt and nonce (we can not guarantee the incrementing anyway). Note that any str objects are assumed to be in utf-8."""
    salt = pysodium.randombytes(pysodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES)
    memlimit = pysodium.crypto_pwhash_scryptsalsa208sha256_MEMLIMIT_INTERACTIVE
    opslimit = pysodium.crypto_pwhash_scryptsalsa208sha256_OPSLIMIT_INTERACTIVE
    if isinstance(password, str): password = password.encode("utf-8")
    key = pysodium.crypto_pwhash_scryptsalsa208sha256(pysodium.crypto_secretbox_KEYBYTES, password, salt, memlimit=memlimit, opslimit=opslimit)
    nonce = pysodium.randombytes(pysodium.crypto_secretbox_NONCEBYTES)
    if isinstance(plaintext, str): plaintext = plaintext.encode("utf-8")
    cyphertext = pysodium.crypto_secretbox(plaintext, nonce, key)
    data = (1).to_bytes(1, "little")
    data += memlimit.to_bytes(4, "little")
    data += opslimit.to_bytes(4, "little")
    data += salt
    data += nonce
    data += cyphertext
    return base64.b64encode(data)
    
def decrypt(cyphertext, password, decode_as="utf-8"):
    data = base64.b64decode(cyphertext)
    version = data[0]
    if version == 1:
        decrypted = scrypt_decrypt(data[1:], password)
    else: raise ValueError("Unknown version %s"%version)
    if decode_as:
        decrypted = decrypted.decode(decode_as)
    return decrypted

def scrypt_decrypt(data, password):
    buf = io.BytesIO(data)
    memlimit = int.from_bytes(buf.read(4), "little")
    opslimit = int.from_bytes(buf.read(4), "little")
    salt = buf.read(pysodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES)
    if isinstance(password, str): password = password.encode("utf-8")
    key = pysodium.crypto_pwhash_scryptsalsa208sha256(pysodium.crypto_secretbox_KEYBYTES, password, salt, memlimit=memlimit, opslimit=opslimit)
    nonce = buf.read(pysodium.crypto_secretbox_NONCEBYTES)
    cyphertext = buf.read()
    return pysodium.crypto_secretbox_open(cyphertext, nonce, key)
