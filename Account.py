import hashlib
import re
import time 

ACCOUNT_FILE = 'user_accounts.txt'
FAILED_ATTEMPTS = {}
MAX_ATTEMPTS = 5 # <-- This sets the 5-try limit
LOCKOUT_DURATION = 300 # 5 minutes in seconds

# --- File Handling ---

def load_accounts():
    accounts = {}
    try:
        with open(ACCOUNT_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    u, p_hash, e = parts
                    accounts[u] = {'password_hash': p_hash, 'email': e}
    except FileNotFoundError:
        pass
    return accounts

def save_accounts(accounts):
    lines = [f"{u},{data['password_hash']},{data['email']}\n" 
             for u, data in accounts.items()]
    with open(ACCOUNT_FILE, 'w') as f:
        f.writelines(lines)

# --- Security & Validation ---

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

# --- Core Logic (Highly Condensed) ---

def sign_up():
    accounts = load_accounts()
    print("\n--- Sign Up ---")
    
    while True:
        username = input("Username: ").strip()
        if not username or username in accounts or ',' in username: continue
        break

    while True:
        password = input("Password (min 6): ")
        if len(password) >= 6:
            hashed_pwd = hash_password(password)
            break
        print("Password too short.")

    while True:
        email = input("Email: ").strip()
        if validate_email(email) and ',' not in email: break
        print("Invalid email.")

    accounts[username] = {'password_hash': hashed_pwd, 'email': email}
    save_accounts(accounts)
    print(f"'{username}' created.")

def log_in():
    """Handles user log-in with 5-try lockout."""
    accounts = load_accounts()
    print("\n--- Log In ---")
    
    username = input("Username: ").strip()
    password = input("Password: ")

    # Check Lockout Status
    if username in FAILED_ATTEMPTS and FAILED_ATTEMPTS[username]['count'] >= MAX_ATTEMPTS:
        if time.time() - FAILED_ATTEMPTS[username]['lockout_time'] < LOCKOUT_DURATION:
            print("Locked out.")
            return None
        else:
            FAILED_ATTEMPTS.pop(username)
                
    if username not in accounts:
        print("Login failed.")
        return None 

    # Authenticate
    if hash_password(password) == accounts[username]['password_hash']:
        print(f"Welcome, {username}.")
        if username in FAILED_ATTEMPTS: FAILED_ATTEMPTS.pop(username)
        user_data = accounts[username].copy()
        user_data.pop('password_hash')
        return user_data
    else:
        print("Login failed.")
        
        # Update attempts
        if username not in FAILED_ATTEMPTS:
            FAILED_ATTEMPTS[username] = {'count': 0, 'lockout_time': 0}
            
        FAILED_ATTEMPTS[username]['count'] += 1
        
        # Check if 5 attempts are reached
        if FAILED_ATTEMPTS[username]['count'] >= MAX_ATTEMPTS:
            FAILED_ATTEMPTS[username]['lockout_time'] = time.time()
            print(f"Max attempts reached. Locked out for 5 minutes.")
            
        return None

# --- Main Execution ---

if __name__ == "__main__":
    print("# Account Operations (1: Sign Up | 2: Log In)")
    choice = input("Enter 1 or 2: ")

    if choice == '1':
        sign_up()
    elif choice == '2':
        user = log_in()
        print(f"Result: {user}")
    else:
        print("Invalid choice.")