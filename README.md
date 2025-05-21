# 🔐 Password Authentication System

A simple, modular, and beginner-friendly Python application that simulates a basic username-password authentication system. This CLI-based tool helps understand fundamental concepts of secure user login, password masking, and validation workflows — ideal for students and educators exploring user authentication logic in Python.

---

## 📌 Overview

This program implements a console-driven password authentication system where users can log in using a predefined username and password combination. It features masked password entry, user feedback, and limited retry attempts.

---

## ✨ Features

- 🔑 **User Login Prompt**
  - Requests both username and password.
  - Password entry is hidden using `getpass` for security.

- 🔁 **Limited Login Attempts**
  - Allows up to 3 attempts before access is denied.

- 🛡️ **Secure Practices**
  - Password is not echoed to the terminal.
  - Uses Python’s built-in `getpass` for security best practices.

- ✅ **Authentication Feedback**
  - Informs user whether login was successful or not.
  - Graceful messaging for failed attempts.

---

## 🧰 Technologies Used

- Python Standard Library:
  - `getpass`: For secure password input.
  - `time`: Optional — can be used to simulate delays (not currently used but good for learning extensions).

---

## ▶️ How to Run

1. **Make sure you have Python 3 installed**:
   ```bash
   python --version
   ```

2. **Run the script**:
   ```bash
   python password-authentication-system.py
   ```

3. **Follow the prompts**:
   - Enter the correct **username** and **password** (defaults are hardcoded in the script).
   - You have **3 attempts** to log in successfully.

---

## 🧪 Sample Output

```
Enter your username: admin
Enter your password:
Login successful!
```

Or, if incorrect:

```
Enter your username: guest
Enter your password:
Incorrect credentials. 2 attempts left.
...
Too many failed attempts. Access denied.
```

---

## 🔍 Customization

You can change the default credentials directly in the script:
```python
USERNAME = "admin"
PASSWORD = "password123"
```

Feel free to enhance the script by:
- Adding a registration system.
- Encrypting stored passwords.
- Logging login attempts.
- Using a file or database for storing user credentials.

---

## 🎓 Learning Highlights

This project demonstrates:
- Basic user authentication logic
- Secure password input with `getpass`
- Control flow with loops and conditionals
- Error messaging and retry logic

---

## 📁 File Structure

```
📦 password-authentication-system
 └── password-authentication-system.py
```

---

## 🚀 Getting Started

No installation or external dependencies required.  
Just run it with Python 3 — great for beginners and quick demos!
