# main.py

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