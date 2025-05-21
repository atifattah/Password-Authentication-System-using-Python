# Import necessary libraries
import getpass
import json
import re
import os
import bcrypt
import random
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv 

# Loading environment variables from .env file
load_dotenv()

class PasswordAuthenticator:
    def __init__(self, db_file="user_database.json"):
        self.db_file = db_file
        self.max_failed_attempts = 5
        self.lockout_duration = 15 
        self.load_database()
    
    def load_database(self):
        """Loading user database from JSON file or create if it doesn't exist."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.database = json.load(f)
        else:
            self.database = {}
            self.save_database()
    
    def save_database(self):
        """Saving user database to JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.database, f, indent=4)
    
    def register_user(self):
        """Registering a new user with email verification."""
        print("\n=== User Registration ===")
        
        # Getting username
        while True:
            username = input("Enter username (min 4 chars, letters/numbers/dots/underscores only): ")
            if len(username) < 4:
                print("Username too short!")
                continue
            if not re.match(r'^[a-zA-Z0-9._]+$', username):
                print("Username contains invalid characters!")
                continue
            if username in self.database:
                print("Username already exists!")
                continue
            break
        
        # Getting and validating email
        while True:
            email = input("Enter email address: ")
            # A basic email validation - in a production app, you'd want to verify this email
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                print("Invalid email format!")
                continue
            
            # Send verification code to the provided email
            print("\nSending verification code to your email...")
            verification_code = self.send_verification_code(email)
            
            # Give the user 3 attempts to enter the correct verification code
            for attempt in range(3):
                user_code = input("Enter the verification code sent to your email: ")
                if user_code == verification_code:
                    print("Email verified successfully!")
                    break
                else:
                    attempts_left = 2 - attempt
                    if attempts_left > 0:
                        print(f"Invalid code! {attempts_left} attempts remaining.")
                    else:
                        print("Too many incorrect verification code attempts.")
                        return False
            else:
                # This will execute if the for loop completes without a break
                return False
            
            # If we get here, email verification was successful
            break
        
        # Getting and validating password
        while True:
            password = getpass.getpass("Create password (min 8 chars, must include uppercase, lowercase, number): ")
            if len(password) < 8:
                print("Password too short!")
                continue
            if not re.search(r'[A-Z]', password):
                print("Password must contain at least one uppercase letter!")
                continue
            if not re.search(r'[a-z]', password):
                print("Password must contain at least one lowercase letter!")
                continue
            if not re.search(r'[0-9]', password):
                print("Password must contain at least one number!")
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("Passwords don't match!")
                continue
            break
        
        # Hashing the password with bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Creating user entry
        self.database[username] = {
            "password_hash": hashed_password.decode('utf-8'),
            "email": email,
            "failed_attempts": 0,
            "locked_until": None,
            "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_database()
        print(f"\nUser {username} registered successfully!")
        return True
    
    def check_account_lockout(self, username):
        """Checking if an account is locked due to too many failed attempts."""
        user_data = self.database.get(username)
        if not user_data:
            return False
        
        if user_data.get("locked_until"):
            lock_time = datetime.strptime(user_data["locked_until"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < lock_time:
                remaining = (lock_time - datetime.now()).total_seconds() / 60
                print(f"Account is locked! Try again in {remaining:.1f} minutes.")
                return True
            else:
                # Resetting failed attempts after lockout period
                user_data["failed_attempts"] = 0
                user_data["locked_until"] = None
                self.save_database()
        return False
    
    def send_verification_code(self, email, username=None):
        """Sending a verification code to the user's email."""
        # Generating a 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Email configuration
        use_simulation = os.environ.get('USE_EMAIL_SIMULATION', 'true').lower() == 'true'
        
        # Always send to the actual user email now (removing test recipient override)
        recipient_email = email
        
        if use_simulation:
            # Simulation mode output
            print("\n" + "="*40)
            print("EMAIL SIMULATION MODE")
            print("="*40)
            print(f"TO: {recipient_email}")
            print(f"SUBJECT: Your Authentication Code")
            print("\nHello,")
            print(f"\nYour verification code is: {code}")
            print("\nThis code will expire in 10 minutes.")
            print("\nBest regards,")
            print("Password Authentication System")
            print("="*40 + "\n")
            return code
        
        # Real email mode
        sender_email = os.environ.get('EMAIL_SENDER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print("Email configuration not found in environment variables.")
            return self._fallback_verification(code, recipient_email)
        
        try:
            # Importing necessary libraries
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            print(f"\nSending email to {recipient_email}...")
            
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = os.environ.get('EMAIL_SUBJECT', "Your Authentication Code")
            
            body = f"""
    Hello {username},

    Your verification code is: {code}

    This code will expire in 10 minutes.

    If you didn't request this code, please ignore this email.

    Best regards,
    Password Authentication System
    """
            
            message.attach(MIMEText(body, "plain"))
            
            # Connecting using port 587 (TLS) which is more reliable than 465 (SSL)
            server = smtplib.SMTP(os.environ.get('SMTP_SERVER', "smtp.gmail.com"), 
                                int(os.environ.get('SMTP_PORT', 587)))
            server.starttls()  
            
            print("Attempting to log in to email server...")
            server.login(sender_email, sender_password)
            
            print("Sending message...")
            server.sendmail(sender_email, recipient_email, message.as_string())
            
            print("Closing connection...")
            server.quit()
            
            print(f"Verification code sent successfully to {recipient_email}")
            return code
        
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return self._fallback_verification(code, recipient_email)
    
    def _fallback_verification(self, code, recipient_email):
        """Fallback method when email sending fails."""
        print("\n" + "="*40)
        print("EMAIL DELIVERY FAILED - SHOWING CODE")
        print("="*40)
        print(f"TO: {recipient_email}")
        print(f"Your verification code is: {code}")
        print("="*40 + "\n")
        return code
    
    def authenticate(self):
        """Authenticating a user with 2FA."""
        print("\n=== User Login ===")
        
        username = input("Enter username: ")
        
        # Checking if username exists
        if username not in self.database:
            print("Username doesn't exist!")
            return False
        
        # Checking if account is locked
        if self.check_account_lockout(username):
            return False
        
        password = getpass.getpass("Enter your password: ")
        user_data = self.database[username]
        
        # Checking password using bcrypt
        password_match = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password_hash"].encode('utf-8')
        )
        
        if not password_match:
            # Increment failed attempts
            user_data["failed_attempts"] += 1
            
            # Checking if we need to lock the account
            if user_data["failed_attempts"] >= self.max_failed_attempts:
                lock_time = datetime.now() + timedelta(minutes=self.lockout_duration)
                user_data["locked_until"] = lock_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Too many failed attempts! Account locked for {self.lockout_duration} minutes.")
            else:
                attempts_left = self.max_failed_attempts - user_data["failed_attempts"]
                print(f"Incorrect password! {attempts_left} attempts remaining.")
            
            self.save_database()
            return False
        
        # Resetting failed attempts on successful password entry
        user_data["failed_attempts"] = 0
        self.save_database()
        
        # Two-factor authentication
        print("\nTwo-factor authentication required!")
        verification_code = self.send_verification_code(user_data["email"], username)
        
        # In a real application, give the user a few attempts to enter the correct code
        for attempt in range(3):
            user_code = input("Enter the verification code sent to your email: ")
            if user_code == verification_code:
                print(f"\nWelcome to the system, {username}!")
                return True
            else:
                print(f"Invalid code! {2-attempt} attempts remaining.")
        
        print("Too many incorrect verification code attempts.")
        return False
    
    def reset_password(self):
        """Reset a user's password with email verification."""
        print("\n=== Password Reset ===")
        
        username = input("Enter your username: ")
        if username not in self.database:
            print("Username doesn't exist!")
            return False
        
        # Check if account is locked
        if self.check_account_lockout(username):
            return False
        
        user_data = self.database[username]
        email = user_data["email"]
        
        # Send verification code to user's email
        verification_code = self.send_verification_code(email)
        
        user_code = input("Enter the verification code sent to your email: ")
        if user_code != verification_code:
            print("Invalid verification code!")
            return False
        
        # Setting new password
        while True:
            new_password = getpass.getpass("Enter new password (min 8 chars, must include uppercase, lowercase, number): ")
            if len(new_password) < 8:
                print("Password too short!")
                continue
            if not re.search(r'[A-Z]', new_password):
                print("Password must contain at least one uppercase letter!")
                continue
            if not re.search(r'[a-z]', new_password):
                print("Password must contain at least one lowercase letter!")
                continue
            if not re.search(r'[0-9]', new_password):
                print("Password must contain at least one number!")
                continue
            
            confirm_password = getpass.getpass("Confirm new password: ")
            if new_password != confirm_password:
                print("Passwords don't match!")
                continue
            break
        
        # Updating password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        user_data["password_hash"] = hashed_password.decode('utf-8')
        user_data["failed_attempts"] = 0
        user_data["locked_until"] = None
        self.save_database()
        
        print("\nPassword reset successful!")
        return True
    
    def populate_demo_users(self):
        """Add ingsome demo users to the system."""
        if self.database:
            print("Database already contains users. Skipping demo users creation.")
            return
            
        demo_users = {
            "user1": {
                "email": "user1@example.com",
                "password": "Password123"
            },
            "admin": {
                "email": "admin@example.com",
                "password": "Admin123456"
            }
        }
        
        for username, data in demo_users.items():
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), salt)
            
            self.database[username] = {
                "password_hash": hashed_password.decode('utf-8'),
                "email": data["email"],
                "failed_attempts": 0,
                "locked_until": None,
                "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        self.save_database()
        print("Demo users created successfully!")

def main():
    auth = PasswordAuthenticator()
    
    # Creating demo users if database is empty
    auth.populate_demo_users()
    
    while True:
        print("\n==== Password Authentication System ====")
        print("1. Login")
        print("2. Register")
        print("3. Reset Password")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            auth.authenticate()
        elif choice == '2':
            auth.register_user()
        elif choice == '3':
            auth.reset_password()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()