# 1. Import the Account module
import Account

def run_application():
    """Main application logic."""
    print("Welcome to the User Management System!")
    print("1: Sign Up (Create Account)")
    print("2: Log In (Access Account)")
    print("3: Exit")

    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == '1':
        # 2. Call the sign_up function from the Account module
        Account.sign_up()

    elif choice == '2':
        # 3. Call the log_in function from the Account module
        user_data = Account.log_in()

        if user_data:
            print(f"\nAuthenticated user data: {user_data}")
            # Start the rest of your application here (e.g., load user profile, main menu)
        else:
            print("\nReturning to main menu.")

    elif choice == '3':
        print("Thank you for using the application. Goodbye!")
        return

    else:
        print("Invalid choice. Please try again.")

    # Simple loop to keep the application running after an action
    print("-" * 30)
    run_application()


# Start the application
if __name__ == "__main__":
    run_application()


    