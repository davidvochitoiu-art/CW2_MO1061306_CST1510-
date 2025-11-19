import pandas as pd
# Import the necessary functions and variables from Account.py
from Account import sign_up, log_in, load_accounts, save_accounts

# You can define global variables or functions for your main application here.

def application_main_features(user_data):
    """
    This function represents the core application features 
    that a user can access AFTER a successful login.
    """
    print("\n==================================")
    print("ACCESS GRANTED TO MAIN FEATURES ")
    print(f"Welcome back, {user_data.get('email')}!")
    print("----------------------------------")
    print("... (Run your main application logic here) ...")
    # For example, a loop for accessing resources, creating items, etc.
    # For now, we'll just return to exit.
    pass


def run_application():
    """Main application loop to handle sign-in/login."""
    
    current_user = None

    while current_user is None:
        print("\n--- Main Application Menu ---")
        print("1: Sign Up (Create New Account)")
        print("2: Log In (Access App)")
        print("3: Exit Application")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            # Call the sign_up function imported from Account.py
            sign_up()
            
        elif choice == '2':
            # Call the log_in function imported from Account.py
            # The result (user dictionary or None) is stored in current_user
            current_user = log_in() 
            
            if current_user:
                # If login is successful, break the loop and proceed to main features
                break
                
        elif choice == '3':
            print("Exiting application. Goodbye!")
            return # Exit the run_application function
            
        else:
            print("Invalid choice. Please try again.")

    # If the loop breaks (successful login), run the main features
    if current_user:
        application_main_features(current_user)

# Guard to run the application when main.py is executed
if __name__ == "__main__":
    run_application()


    import sqlite3
# Establish a global connection
conn = sqlite3.connect('user_accounts.db')

# === FIX for NameError: DEFINE create_user_table() first ===
def create_user_table():
    """Creates the 'users' table if it doesn't already exist."""
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT DEFAULT 'user' ) """)
    conn.commit()

# === CALL create_user_table() second (to initialize the database) ===
create_user_table()


# Corrected 'add_user' function
def add_user(name, password_hash, role='user'):
    """Inserts a new user into the database."""
    cursor = conn.cursor()
    # Correct SQL and parameter binding
    sql = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
    params = (name, password_hash, role) 
    cursor.execute(sql, params)
    conn.commit()

# Corrected 'get_users' function
def get_users():
    """Retrieves all users from the database."""
    cursor = conn.cursor()
    sql = "SELECT * FROM users"
    cursor.execute(sql)
    users = cursor.fetchall()
    return users
 

# Corrected 'migrate_user_data' function
def migrate_user_data():
    """Reads users from a plaintext file and inserts them into the database."""
    try:
        # NOTE: This assumes 'user_accounts.db' is a plaintext file, NOT the SQLite database itself
        with open("user_accounts.db", "r") as f:
            users = f.readlines()
        for user in users:
            try:
                name, password_hash = user.strip().split(',')
                # Correct call to the fixed add_user function
                add_user(name, password_hash)
            except ValueError:
                print(f"Skipping malformed user line: {user.strip()}")
    except Exception as e:
        print(f"Migration error: {e}")