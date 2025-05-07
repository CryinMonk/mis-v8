# Management Information System (MIS)

A secure multi-user management information system built with PyQt5 and SQLAlchemy ORM.

## Features

- Secure user authentication with encrypted passwords
- Role-Based Access Control (RBAC)
- MySQL database integration via SQLAlchemy ORM
- Support for 4 admin user types (admin, data warehouse, teacher, supervisor)
- Concurrent session management
- Login attempt monitoring and account lockout protection
- Encrypted data storage
- Modern PyQt5 user interface

## System Requirements

- Python 3.7+
- MySQL server (XAMPP recommended for development)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mis-project.git
cd mis-project
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the MySQL database:
   - Start XAMPP and ensure MySQL server is running
   - Create a new database named `mis_db`
   - Update database connection settings in `config.json` if needed

5. Initialize the database:
```bash
python scripts/init_database.py
```

6. Run the application:
```bash
python main.py
```

## Default Login Credentials

The system is initialized with the following default users:
- **Admin**: username=admin, password=Admin@123
- **Data Warehouse**: username=datawarehouse, password=Data@123
- **Teacher**: username=teacher, password=Teacher@123
- **Supervisor**: username=supervisor, password=Super@123

**Important**: It is recommended to change these passwords after initial login.

## Project Structure

```
mis_project/
├── app/                    # Main application code
│   ├── config/             # Configuration management
│   ├── controllers/        # Business logic controllers
│   ├── models/             # Data models
│   ├── services/           # Service layer
│   ├── ui/                 # PyQt5 UI components
│   ├── utils/              # Utility functions
│   └── database/           # Database connection management
├── scripts/                # Utility scripts
├── logs/                   # Log files directory
├── tests/                  # Test files
├── config.json             # Application configuration
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Security Features

- Password hashing using bcrypt
- Session management with secure token generation
- Account lockout after multiple failed attempts
- Role-based permissions enforcement
- Configuration encryption for sensitive data
- Secure concurrent session handling
- Comprehensive logging

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details."# mis-v8" 
