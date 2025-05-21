# ⚙️ Setup Guide: Preparing to Run the Password Authentication System

Follow these steps to configure your environment so the script can send real email verification codes using Gmail.

---

## ✉️ Step 1: Enable Two-Factor Authentication on Your Google Account

Google requires App Passwords only if 2FA is enabled.

1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Under **"Signing in to Google"**, enable **2-Step Verification**
3. Once enabled, you'll see an **"App passwords"** option

---

## 🔑 Step 2: Generate a Gmail App Password

1. Visit [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. You may need to re-enter your Google credentials
3. Choose:
   - **App**: "Mail"
   - **Device**: "Other (Custom name)" → Enter: `PasswordAuthSystem`
4. Click **Generate**
5. Copy the **16-character App Password** Google provides. You will need this in the next step.

---

## 🛠️ Step 3: Install Required Python Libraries

Use `pip` to install dependencies:

```bash
pip install bcrypt python-dotenv
```

---

## 🧾 Step 4: Create a `.env` File

Create a file named `.env` in the same directory as your script. Paste the following and update with your credentials:

```ini
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=your16charapppassword
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SUBJECT=Your Authentication Code
USE_EMAIL_SIMULATION=false
```

💡 Tip: If you're just testing and don’t want to send real emails yet, set:
```ini
USE_EMAIL_SIMULATION=true
```

---

## ✅ Step 5: Verify Directory Contents

Ensure your project directory looks like this:

```
📁 password-authentication-system
 ├── password-authentication-system.py
 ├── .env
 └── user_database.json   # auto-created after first run
```

---

## 🚀 Step 6: Run the Application

```bash
python password-authentication-system.py
```

You'll now be able to register, log in, and reset passwords — with email verification powered by Gmail!

---

## 📌 Common Issues

- **Email not sent?**
  - Double-check your `.env` values
  - Make sure 2FA is enabled and App Password is used
- **App Password rejected?**
  - Try revoking and regenerating a new App Password from the Google page

---

## 🧪 Development Mode (Simulation)

If you're just testing, enable simulation mode to avoid sending real emails:

```ini
USE_EMAIL_SIMULATION=true
```

Verification codes will be printed in the console instead of being emailed.

---

That's it! You’re now ready to run your own secure authentication system.
