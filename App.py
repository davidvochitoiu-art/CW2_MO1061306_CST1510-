import streamlit as st
import pandas as pd
import plotly.express as px
import Account
import builtins
from io import StringIO
import sys

# Define page_title
page_title = "My App Title - " 

st.set_page_config(
    page_title=page_title + "CST1510 - IT Operations",
    layout="wide"
)

# --- 1. Session State and Helper Class for Input/Output Patching ---

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login' # Start at Login page

# Class to mock the command-line input() function
class MockInput:
    """A callable class to replace builtins.input() with a sequence of stored values."""
    def __init__(self, data_list):
        self.data_list = data_list
        self.index = 0

    def __call__(self, prompt=''):
        """Called when Account.py uses input()."""
        if self.index >= len(self.data_list):
            raise EOFError("MockInput ran out of data.")
        
        # Display the prompt to the user in the Streamlit console for debugging
        # st.toast(f"Mocking input for prompt: {prompt}")
        
        value = self.data_list[self.index]
        self.index += 1
        return value

def run_account_function(func, input_data_list):
    """
    Patches input() and stdout, runs the Account function, and restores original settings.
    Returns: A dictionary containing the captured output and the result of the function.
    """
    original_input = builtins.input
    original_stdout = sys.stdout
    
    # 1. Patch input() with our mock data sequence
    builtins.input = MockInput(input_data_list)
    
    # 2. Patch stdout to capture print() calls
    captured_output = StringIO()
    sys.stdout = captured_output
    
    result = None
    try:
        # 3. Execute the function from Account.py
        result = func()
    except EOFError:
        # This handles cases where Account.py loops asking for input 
        # (e.g., failed validation) more times than we supplied data.
        st.error("Input data exhausted. Login/Signup failed due to internal validation.")
    finally:
        # 4. Restore original input/stdout
        builtins.input = original_input
        sys.stdout = original_stdout
        
    return {
        'result': result,
        'output': captured_output.getvalue()
    }

# --- 2. Streamlit Handler Functions ---

def handle_login(username, password):
    """Feeds username and password into Account.log_in() and processes the result."""
    input_data = [username, password]
    
    response = run_account_function(Account.log_in, input_data)
    user_data = response['result']
    
    if user_data:
        st.session_state['logged_in'] = True
        st.session_state['user_data'] = user_data
        st.session_state['page'] = 'App'
        st.success(f"Successfully logged in! Welcome.")
        st.rerun() # FIX: Changed from st.experimental_rerun() to st.rerun()
    else:
        st.error(f"Login Failed. Output from Account.py: \n\n{response['output']}")
        
def handle_signup(username, email, password):
    """Feeds details into Account.sign_up() and processes the result."""
    # Input order: username, password, email (based on your Account.py)
    input_data = [username, password, email]
    
    response = run_account_function(Account.sign_up, input_data)
    
    if "successfully created and stored!" in response['output']:
        st.success(f"Account created successfully for {username}! Please log in.")
        st.session_state['page'] = 'Login'
        st.rerun() # FIX: Changed from st.experimental_rerun() to st.rerun()
    else:
        st.error(f"Sign Up Failed. Output from Account.py: \n\n{response['output']}")
        
def handle_logout():
    st.session_state['logged_in'] = False
    st.session_state['user_data'] = None
    st.session_state['page'] = 'Login'
    st.rerun() # FIX: Changed from st.experimental_rerun() to st.rerun()

# --- 3. Streamlit Page Rendering Functions ---

def render_login_page():
    st.header("Account Log In")
    with st.form("login_form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if username and password:
                handle_login(username, password)
            else:
                st.warning("Please enter both username and password.")

    st.markdown("---")
    if st.button("Need an account? Sign Up"):
        st.session_state['page'] = 'Signup'
        st.rerun() # FIX: Changed from st.experimental_rerun() to st.rerun()

def render_signup_page():
    st.header("New Account Sign Up")
    with st.form("signup_form"):
        new_username = st.text_input("Choose a Username").strip()
        # Input order MUST match Account.py: password then email
        new_password = st.text_input("Create a Password (min 6 characters)", type="password")
        new_email = st.text_input("Enter your Email").strip()
        submitted = st.form_submit_button("Create Account")

        if submitted:
            if not all([new_username, new_email, new_password]):
                st.warning("All fields are required.")
            else:
                handle_signup(new_username, new_email, new_password)
                
    st.markdown("---")
    if st.button("Already have an account? Log In"):
        st.session_state['page'] = 'Login'
        st.rerun() # FIX: Changed from st.experimental_rerun() to st.rerun()

def render_application_content():
    st.header(f"Welcome, {st.session_state['user_data'].get('email', 'User')}!")
    st.info("You are logged in and can access the application features.")
    
    with st.sidebar:
        st.header("Controls")
        option = st.selectbox(
            "Choose an option:",
            ["Dashboard", "Reports", "Settings"]
        )
        st.markdown("---")
        if st.button("Log Out"):
            handle_logout()

    st.write(f"Your selected application view: **{option}**")
    
    st.subheader("Data Visualization Placeholder")
    data = {'Category': ['A', 'B', 'C', 'D'], 'Value': [10, 20, 15, 25]}
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Category', y='Value', title='Sample Data')
    st.plotly_chart(fig, use_container_width=True)

# --- 4. Main App Logic ---

st.title("User Management Integrated App")
st.caption("Powered by the unmodified Account.py")

if st.session_state['logged_in']:
    render_application_content()
else:
    # Render navigation based on the current page state
    if st.session_state['page'] == 'Login':
        render_login_page()
    elif st.session_state['page'] == 'Signup':
        render_signup_page()