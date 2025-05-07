# import os
# import json
# from cryptography.fernet import Fernet
#
#
# class Config:
#     _instance = None
#
#     # Default configuration
#     DEFAULT_CONFIG = {
#         "auth_database": {
#             "host": "localhost",
#             "port": 3306,
#             "database": "mis_db",
#             "username": "root",
#             "password": ""
#         },
#         "data_database": {
#             "host": "localhost",
#             "port": 3306,
#             "database": "pwd_students_db",
#             "username": "root",
#             "password": ""
#         },
#         "security": {
#             "session_timeout_hours": 8,
#             "password_min_length": 8,
#             "password_require_special": True,
#             "password_require_uppercase": True,
#             "password_require_numbers": True,
#             "max_failed_attempts": 5,
#             "lockout_duration_minutes": 30,
#             "encryption_key": ""  # Will be generated if empty
#         },
#         "logging": {
#             "log_level": "INFO",
#             "log_file": "logs/mis_system.log"
#         },
#         "user_info": {
#             "last_login": "admin",
#             "last_login_time": "2025-04-26 07:34:53"
#         }
#     }
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(Config, cls).__new__(cls)
#             cls._instance._load_config()
#         return cls._instance
#
#     def _load_config(self):
#         config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
#
#         # Create default config if doesn't exist
#         if not os.path.exists(config_path):
#             self._create_default_config(config_path)
#
#         # Load config
#         with open(config_path, 'r') as f:
#             self._config = json.load(f)
#
#         # Ensure all required sections exist by merging with defaults
#         self._migrate_config_if_needed()
#
#         # Ensure encryption key exists
#         if not self._config['security']['encryption_key']:
#             key = Fernet.generate_key().decode()
#             self._config['security']['encryption_key'] = key
#             self._save_config(config_path)
#
#     def _migrate_config_if_needed(self):
#         """Make sure config has all required sections, migrating old to new structure if needed"""
#         config_updated = False
#
#         # If old database structure exists but not new structure, migrate
#         if 'database' in self._config and 'auth_database' not in self._config:
#             self._config['auth_database'] = self._config['database'].copy()
#             self._config['data_database'] = self._config['database'].copy()
#             self._config['data_database']['database'] = 'pwd_students_db'
#             config_updated = True
#
#         # Make sure user_info exists
#         if 'user_info' not in self._config:
#             self._config['user_info'] = self.DEFAULT_CONFIG['user_info']
#             config_updated = True
#
#         # Add any missing sections from default config
#         for key, value in self.DEFAULT_CONFIG.items():
#             if key not in self._config:
#                 self._config[key] = value
#                 config_updated = True
#             elif isinstance(value, dict):
#                 for sub_key, sub_value in value.items():
#                     if sub_key not in self._config[key]:
#                         self._config[key][sub_key] = sub_value
#                         config_updated = True
#
#         # Save if updated
#         if config_updated:
#             config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
#             self._save_config(config_path)
#
#     def _create_default_config(self, config_path):
#         # Generate a new encryption key
#         key = Fernet.generate_key().decode()
#         config = self.DEFAULT_CONFIG.copy()
#         config['security']['encryption_key'] = key
#
#         # Ensure directory exists
#         os.makedirs(os.path.dirname(config_path), exist_ok=True)
#
#         with open(config_path, 'w') as f:
#             json.dump(config, f, indent=4)
#
#         # Secure the config file permissions
#         try:
#             os.chmod(config_path, 0o600)  # Read/write for owner only
#         except Exception:
#             print("Warning: Could not set secure permissions on config file")
#
#         self._config = config
#
#     def _save_config(self, config_path):
#         with open(config_path, 'w') as f:
#             json.dump(self._config, f, indent=4)
#
#     def get_auth_db_connection_string(self):
#         # Try to get from auth_database, fall back to database if not available
#         db_config = self._config.get('auth_database', self._config.get('database'))
#         return f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
#
#     def get_data_db_connection_string(self):
#         # Try to get from data_database, fall back to database if not available
#         db_config = self._config.get('data_database', self._config.get('database'))
#         # Override database name if using fallback
#         if 'data_database' not in self._config and db_config['database'] != 'pwd_students_db':
#             db_config = db_config.copy()  # Make a copy to avoid modifying the original
#             db_config['database'] = 'pwd_students_db'
#         return f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
#
#     def get_encryption_key(self):
#         return self._config['security']['encryption_key'].encode()
#
#     @property
#     def session_timeout(self):
#         return self._config['security']['session_timeout_hours']
#
#     @property
#     def password_requirements(self):
#         security = self._config['security']
#         return {
#             'min_length': security['password_min_length'],
#             'require_special': security['password_require_special'],
#             'require_uppercase': security['password_require_uppercase'],
#             'require_numbers': security['password_require_numbers']
#         }
#
#     @property
#     def max_failed_attempts(self):
#         return self._config['security']['max_failed_attempts']
#
#     @property
#     def lockout_duration(self):
#         return self._config['security']['lockout_duration_minutes']
#
#     @property
#     def log_file_path(self):
#         log_file = self._config['logging']['log_file']
#         # Ensure path is absolute
#         if not os.path.isabs(log_file):
#             return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), log_file)
#         return log_file
#
#     @property
#     def log_level(self):
#         return self._config['logging']['log_level']
#
#     @property
#     def current_user(self):
#         return self._config.get('user_info', {}).get('last_login', 'admin')
#
#     def update_last_login(self, username, timestamp):
#         """Update the last login username and timestamp"""
#         if 'user_info' not in self._config:
#             self._config['user_info'] = {}
#         self._config['user_info']['last_login'] = username
#         self._config['user_info']['last_login_time'] = timestamp
#         self._save_config(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json'))

import os
import json
# import datetime
from cryptography.fernet import Fernet


class Config:
    _instance = None

    # Default configuration
    DEFAULT_CONFIG = {
        "auth_database": {
            "host": "localhost",
            "port": 3306,
            "database": "mis_db",
            "username": "root",
            "password": ""
        },
        "data_database": {
            "host": "localhost",
            "port": 3306,
            "database": "pwd_students_db",
            "username": "root",
            "password": ""
        },
        "security": {
            "session_timeout_hours": 8,
            "password_min_length": 8,
            "password_require_special": True,
            "password_require_uppercase": True,
            "password_require_numbers": True,
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 30,
            "encryption_key": ""  # Will be generated if empty
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "logs/mis_system.log"
        },
        "user_info": {
            "last_login": "",
            "last_login_time": ""
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')

        # Create default config if doesn't exist
        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        # Load config
        with open(config_path, 'r') as f:
            self._config = json.load(f)

        # Ensure all required sections exist by merging with defaults
        self._migrate_config_if_needed()

        # Ensure encryption key exists
        if not self._config['security']['encryption_key']:
            key = Fernet.generate_key().decode()
            self._config['security']['encryption_key'] = key
            self._save_config(config_path)

    def _migrate_config_if_needed(self):
        """Make sure config has all required sections, migrating old to new structure if needed"""
        config_updated = False

        # If old database structure exists but not new structure, migrate
        if 'database' in self._config and 'auth_database' not in self._config:
            self._config['auth_database'] = self._config['database'].copy()
            self._config['data_database'] = self._config['database'].copy()
            self._config['data_database']['database'] = 'pwd_students_db'
            config_updated = True

        # Make sure user_info exists
        if 'user_info' not in self._config:
            self._config['user_info'] = self.DEFAULT_CONFIG['user_info'].copy()
            config_updated = True

        # Add any missing sections from default config
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value
                config_updated = True
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self._config[key]:
                        self._config[key][sub_key] = sub_value
                        config_updated = True

        # Save if updated
        if config_updated:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            self._save_config(config_path)

    def _create_default_config(self, config_path):
        # Generate a new encryption key
        key = Fernet.generate_key().decode()
        config = self.DEFAULT_CONFIG.copy()
        config['security']['encryption_key'] = key

        # Initialize user_info with empty values
        config['user_info'] = {
            "last_login": "",
            "last_login_time": ""
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        # Secure the config file permissions
        try:
            os.chmod(config_path, 0o600)  # Read/write for owner only
        except PermissionError:
            print("Warning: Permission denied when trying to set secure permissions on config file")
        except FileNotFoundError:
            print("Warning: Config file not found when trying to set permissions")
        except OSError as e:
            print(f"Warning: OS error when setting config file permissions: {str(e)}")
        except Exception as e:
            print(f"Warning: Unexpected error when setting config file permissions: {str(e)}")

        self._config = config

    def _save_config(self, config_path):
        with open(config_path, 'w') as f:
            json.dump(self._config, f, indent=4)

    def get_auth_db_connection_string(self):
        # Try to get from auth_database, fall back to database if not available
        db_config = self._config.get('auth_database', self._config.get('database'))
        return f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    def get_data_db_connection_string(self):
        # Try to get from data_database, fall back to database if not available
        db_config = self._config.get('data_database', self._config.get('database'))
        # Override database name if using fallback
        if 'data_database' not in self._config and db_config['database'] != 'pwd_students_db':
            db_config = db_config.copy()  # Make a copy to avoid modifying the original
            db_config['database'] = 'pwd_students_db'
        return f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    def get_encryption_key(self):
        return self._config['security']['encryption_key'].encode()

    @property
    def session_timeout(self):
        return self._config['security']['session_timeout_hours']

    @property
    def password_requirements(self):
        security = self._config['security']
        return {
            'min_length': security['password_min_length'],
            'require_special': security['password_require_special'],
            'require_uppercase': security['password_require_uppercase'],
            'require_numbers': security['password_require_numbers']
        }

    @property
    def max_failed_attempts(self):
        return self._config['security']['max_failed_attempts']

    @property
    def lockout_duration(self):
        return self._config['security']['lockout_duration_minutes']

    @property
    def log_file_path(self):
        log_file = self._config['logging']['log_file']
        # Ensure path is absolute
        if not os.path.isabs(log_file):
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), log_file)
        return log_file

    @property
    def log_level(self):
        return self._config['logging']['log_level']

    @property
    def current_user(self):
        # Return empty string if last_login is not available or empty
        return self._config.get('user_info', {}).get('last_login') or ""

    def update_last_login(self, username, timestamp):
        """Update the last login username and timestamp"""
        if 'user_info' not in self._config:
            self._config['user_info'] = {}
        self._config['user_info']['last_login'] = username
        self._config['user_info']['last_login_time'] = timestamp
        self._save_config(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json'))
