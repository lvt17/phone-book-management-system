# Phonebook Management System - Group 02 📱

A professional phonebook management project with a Command Line Interface (CLI), supporting multi-user authentication and data storage with MySQL. This project is the final assignment for **Programming & Testing - Group 02**.

## ✨ Key Features (Phonebook CLI)

### 🔐 User Authentication

- Secure **Register/Login** functionality.
- SHA-256 password encryption.
- Isolated contact space for each user.

### 📞 Contact Management

- **Add/Edit/Delete** contacts with full details (Name, Phone, Email, Address).
- **Search** functionality by name or phone number.
- Professional table display using the `Rich` library.

### 📂 Category Management

- Organize contacts into groups (Family, Work, Friends...).
- Filter contacts by specific categories.

---

## 🛠 Tech Stack

- **Language:** Python 3.10+
- **UI Library:** [Rich](https://github.com/Textualize/rich) (CLI UI)
- **Database:** MySQL 8.0+
- **Connector:** `mysql-connector-python`
- **Containerization:** Docker & Docker Compose support.

---

## 🚀 Getting Started

Detailed installation and usage instructions are available at: [Phonebook_App/README.md](./Phonebook_App/README.md)

### Quick Run with Docker:

```bash
cd Phonebook_App
docker-compose up --build
```

### Manual Run (Local):

1. Install dependencies:
   ```bash
   pip install -r Phonebook_App/requirements.txt
   ```
2. Initialize MySQL database (app handles this automatically for localhost).
3. Run the application:
   ```bash
   python Phonebook_App/main.py
   ```

---

---

© 2024 Programming & Testing - Group 02.
