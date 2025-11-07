import json
import hashlib # It used for secure password hashing for the passwords
import re # Addedd for better Email Validation

# --- File Hndling function ---

def load_accounts():
    """Load all existing account from the JSON file."""
    # FIX: Use 'user_accounts.json' to match save_accounts()
    try:
        with open('user_accounts.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # FIX: Return an empty DICTIONARY {} because accounts are stored as a dict {username: data}
        return {}
    except json.JSONDecodeError:
        # FIX: Return an empty DICTIONARY {} if JSON is malformed
        return {}

def save_accounts(accounts):
    """save the current account data back to the Json File."""
    # This remains correct
    with open('user_accounts.json', 'w') as file:
        # safe with indentation for better readability
        json.dump(accounts, file, indent=4)

# --- Security Helper Functions ---
# ... (rest of the code is correct)

def hash_password(password):
    """Hash the password using the SHA-256 for Security."""
    # Encode the string to bytes, then hash it and return the hexadecimal representation
    return hashlib.sha256(password.encode()).hexdigest()

# --- Validation Functions ---

def validate_email(email):
    """Validate the email format using regex."""
    #  simple regex pattern for basic email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)


def sign_up():
    """Collects new user details (username, email, password), stores them, and saves to file."""
    print("\n--- New Account Sign Up ---")

    accounts = load_accounts()

    # 1. Get Username (must be unique)
    while True:
        username = input("Enter a new username: ").strip()
        if not username:
            print("Username cannot be empty.")
        elif username in accounts:
            print("Username already taken. Please choose another.")
        else:
            break

    # 2. Get Password (simple length check)
    while True:
        password = input("Enter a password (min 6 characters): ")
        if len(password) < 6:
            print("Password is too short. Please enter at least 6 characters.")
        else:
            hashed_pwd = hash_password(password)
            break

    # 3. Get Email (with validation)
    while True:
        email = input("Enter your email: ").strip()
        if not validate_email(email):
            print("Invalid email format. Please try again.")
        else:
            break

    # Store the new account details
    accounts[username] = {
        'password_hash': hashed_pwd,
        'email': email,
    }

    save_accounts(accounts)
    print(f"\nAccount for '{username}' successfully created and stored!")

def log_in():
    """Checks provided credentials against stored data."""
    print("\n--- Account Log In ---")

    accounts = load_accounts()

    username = input("Enter your username: ").strip()
    password = input("Enter your password: ")

    # 1. Check if the username exists
    if username not in accounts:
        print("Login failed: Username not found.")
        return None # Indicate failure

    # 2. Hash the entered password and compare it to the stored hash
    entered_pwd_hash = hash_password(password)
    stored_pwd_hash = accounts[username]['password_hash']

    if entered_pwd_hash == stored_pwd_hash:
        print(f"\nSuccess! Welcome back, {username}.")
        # Return the user's details (excluding the hash) upon successful login
        user_data = accounts[username].copy()
        user_data.pop('password_hash')
        return user_data
    else:
        print("Login failed: Incorrect password.")
        return None # Indicate failure

# --- Main Program Execution ---

if __name__ == "__main__":

    print("# Account details and operations")
    print("Welcome! Choose an option:")
    print("1: Sign Up (Create New Account)")
    print("2: Log In (Access Existing Account)")

    choice = input("Enter 1 or 2: ")

    if choice == '1':
        sign_up()
    elif choice == '2':
        logged_in_user = log_in()

        if logged_in_user:
            print("\n--- Extracted Data (Successful Login) ---")
            print("This data can be used to load user-specific features.")
            print(f"User Data: {logged_in_user}")
            # You would continue the application logic here
        else:
            print("Login attempt complete. Access denied.")
    else:
        print("Invalid choice.")