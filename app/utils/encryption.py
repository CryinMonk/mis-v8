# import base64
# import os
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from app.config.config import Config
#
#
# class Encryption:
#     """Utility class for encryption and decryption of sensitive data"""
#
#     def __init__(self):
#         self.config = Config()
#         self._key = self.config.get_encryption_key()
#         self._cipher = Fernet(self._key)
#
#     def encrypt(self, data):
#         """
#         Encrypt data using the application key
#
#         Args:
#             data: String data to encrypt
#
#         Returns:
#             Encrypted data as a base64-encoded string
#         """
#         if isinstance(data, str):
#             data = data.encode('utf-8')
#
#         encrypted_data = self._cipher.encrypt(data)
#         return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
#
#     def decrypt(self, encrypted_data):
#         """
#         Decrypt data using the application key
#
#         Args:
#             encrypted_data: Base64-encoded encrypted string
#
#         Returns:
#             Decrypted data as string
#         """
#         try:
#             if isinstance(encrypted_data, str):
#                 encrypted_data = base64.urlsafe_b64decode(encrypted_data)
#
#             decrypted_data = self._cipher.decrypt(encrypted_data)
#             return decrypted_data.decode('utf-8')
#         except Exception as e:
#             # Log the error
#             print(f"Decryption error: {str(e)}")
#             return None
#
#     @staticmethod
#     def generate_key(password, salt=None):
#         """
#         Generate encryption key from password and salt
#
#         Args:
#             password: Password to derive key from
#             salt: Optional salt, generated if not provided
#
#         Returns:
#             Tuple containing (key, salt)
#         """
#         if salt is None:
#             salt = os.urandom(16)
#
#         kdf = PBKDF2HMAC(
#             algorithm=hashes.SHA256(),
#             length=32,
#             salt=salt,
#             iterations=100000,
#         )
#
#         key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
#         return key, salt