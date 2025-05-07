# import re
# from app.config.config import Config
#
#
# class PasswordValidator:
#     def __init__(self):
#         self.config = Config()
#         self.requirements = self.config.password_requirements
#
#     def validate(self, password):
#         errors = []
#
#         # Check length
#         if len(password) < self.requirements['min_length']:
#             errors.append(f"Password must be at least {self.requirements['min_length']} characters long.")
#
#         # Check for uppercase letters
#         if self.requirements['require_uppercase'] and not re.search(r'[A-Z]', password):
#             errors.append("Password must contain at least one uppercase letter.")
#
#         # Check for numbers
#         if self.requirements['require_numbers'] and not re.search(r'\d', password):
#             errors.append("Password must contain at least one number.")
#
#         # Check for special characters
#         if self.requirements['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#             errors.append("Password must contain at least one special character.")
#
#         # Check for common passwords
#         common_passwords = ['password', 'admin123', '123456', 'qwerty']
#         if password.lower() in common_passwords:
#             errors.append("This is a commonly used password and is not secure.")
#
#         return errors