import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import sys

# =========================================================
# 1. ITTicket Entity Model 
# =========================================================

class ITTicket:
    """Represents a single IT Service Desk ticket entity."""
    def __init__(self, ticket_id, staff_member, category, status, resolution_time_days):
        self.ticket_id = ticket_id
        self.staff_member = staff_member
        self.category = category
        self.status = status
        try:
            self.resolution_time_days = float(resolution_time_days)
        except (ValueError, TypeError):
            self.resolution_time_days = None

# =========================================================
# 2. ITopDBManager Class (Complete CRUD Layer)
# =========================================================

class ITopDBManager:
    """
    Manages the SQLite connection and CRUD operations for the IT tickets table.
    (This was previously split between your files)
    """
    DB_PATH = "multi_domain_platform.db"
    TABLE_NAME = "it_tickets"

    def __init__(self):
        self._create_table()

    def _execute_query(self, query, params=()):
        """Internal helper for executing queries."""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.Error as e:
            if 'streamlit' in st.__dict__:
                 st.error(f"Database Error: {e}")
            else:
                 print(f"Database Error: {e}") 
        finally:
            conn.close()

    def _create_table(self):
        """Creates the 'it_tickets' table if it doesn't already exist."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            ticket_id INTEGER PRIMARY KEY,
            staff_member TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution_time_days REAL
        );
        """
        self._execute_query(create_table_query)

    # --- CREATE (User Input) METHOD ---
    def add_new_ticket(self, staff_member, category, status):
        """Inserts a new ticket record into the database based on user input."""
        query = f"""
        INSERT INTO {self.TABLE_NAME} 
        (ticket_id, staff_member, category, status, resolution_time_days) 
        VALUES (NULL, ?, ?, ?, NULL);
        """
        params = (staff_member, category, status)
        self._execute_query(query, params)
    
    # --- UPDATE (Analysis Prep) METHOD - ADDED FIX ---
    def resolve_ticket(self, ticket_id, resolution_time_days):
        """Updates a ticket's status to 'Resolved' and sets the resolution time."""
        query = f"""
        UPDATE {self.TABLE_NAME}
        SET status = 'Resolved', resolution_time_days = ?
        WHERE ticket_id = ?;
        """
        params = (resolution_time_days, ticket_id)
        self._execute_query(query, params)

    # --- READ (Analysis/Export) METHOD ---
    def read_all_tickets(self):
        """Reads all records and returns them as a Pandas DataFrame for analysis."""
        conn = sqlite3.connect(self.DB_PATH)
        try:
            df = pd.read_sql_query(f"SELECT * FROM {self.TABLE_NAME}", conn)
            return df
        except pd.io.sql.DatabaseError:
            return pd.DataFrame()
        finally:
            conn.close()

# =========================================================
# 3. Analysis Logic 
# =========================================================

def get_service_desk_bottleneck_analysis():
    """Analyzes IT ticket data to identify bottlenecks."""
    db_manager = ITopDBManager()
    df = db_manager.read_all_tickets()
    
    if df.empty:
        return None, None, None, None
    
    df['resolution_time_days'] = pd.to_numeric(df['resolution_time_days'], errors='coerce')
    resolved_df = df[df['status'] == 'Resolved'].dropna(subset=['resolution_time_days']).copy()

    # Staff Performance Anomaly (Avg Resolution Time)
    staff_performance_df = resolved_df.groupby('staff_member')['resolution_time_days'].mean().reset_index(name='Avg Resolution Time (Days)').sort_values(by='Avg Resolution Time (Days)', ascending=False)
    
    # Process Inefficiency (Status Causing Delay)
    bottleneck_statuses = ['Waiting for User', 'Pending Vendor', 'On Hold']
    status_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('status').agg(Tickets_Stuck=('ticket_id', 'count')).reset_index().sort_values(by='Tickets_Stuck', ascending=False)
    
    # Staff Workload and Merge
    staff_workload_df = resolved_df.groupby('staff_member').agg(Tickets_Handled=('ticket_id', 'count')).reset_index()
    staff_performance_df = staff_performance_df.merge(staff_workload_df, on='staff_member', how='left').fillna(0)
    
    # Categorical Root Cause Analysis
    category_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('category').agg(Tickets_Stuck=('ticket_id', 'count')).reset_index().sort_values(by='Tickets_Stuck', ascending=False)
        
    return staff_performance_df, status_bottleneck_df, staff_workload_df, category_bottleneck_df

# =========================================================
# 4. Streamlit Input Form (User Interface)
# =========================================================

def display_ticket_entry_form():
    """Renders the form for end-users to input new IT ticket data."""
    st.title("➕ New IT Ticket Entry")
    db_manager = ITopDBManager()

    STAFF_MEMBERS = ['Alice', 'Bob', 'Charlie', 'Dana', 'Admin']
    CATEGORIES = ['Hardware Request', 'Software Access', 'Network Issue', 'Printer Issue', 'Password Reset']
    INITIAL_STATUS = ['New']

    with st.form("new_ticket_form"):
        st.header("Ticket Details")
        
        staff_member = st.selectbox("Staff Member Assigned:", STAFF_MEMBERS)
        category = st.selectbox("Ticket Category:", CATEGORIES)
        status = st.selectbox("Initial Status:", INITIAL_STATUS)
        
        submitted = st.form_submit_button("Log New Ticket")

        if submitted:
            try:
                db_manager.add_new_ticket(staff_member, category, status)
                st.success(f"Ticket logged successfully! Status: {status}")
                st.balloons()
                
            except Exception as e:
                st.error(f"Failed to log ticket. Database error: {e}")

# =========================================================
# 5. Streamlit Dashboard View
# =========================================================

def display_itop_dashboard():
    """Renders the analysis dashboard using Plotly visualizations."""
    st.title("👨‍🔧 IT Operations Service Desk Analytics")
    
    staff_delay, status_delay, status_workload, category_delay = get_service_desk_bottleneck_analysis()
    
    if staff_delay is None or staff_delay.empty:
        st.warning("🚨 No data found or no tickets are marked 'Resolved' with a valid resolution time. Please enter tickets and run the update script.")
        return
    
    # --- Visualizations ---
    st.header("1. Staff Performance Anomaly")
    
    fig1 = px.bar(
        staff_delay.head(5), 
        x='staff_member', 
        y='Avg Resolution Time (Days)',
        color='Tickets_Handled', 
        title='Top 5 Staff by Average Resolution Time'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.header("2. Process & Categorical Bottlenecks")
    
    if not status_delay.empty:
        fig2 = px.pie(
            status_delay, 
            values='Tickets_Stuck', 
            names='status', 
            title='Volume of Tickets in Non-Resolving Statuses'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    if not category_delay.empty:
        fig3 = px.bar(
            category_delay, 
            x='category', 
            y='Tickets_Stuck', 
            title='Categories Causing Most Delays',
            color='Tickets_Stuck'
        )
        st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# 6. Main Application Control
# =========================================================

def main():
    st.sidebar.title("IT Operations Menu")
    
    selected_page = st.sidebar.radio(
        "Navigation",
        ["Dashboard & Analysis", "New Ticket Entry"]
    )

    if selected_page == "New Ticket Entry":
        display_ticket_entry_form()
    elif selected_page == "Dashboard & Analysis":
        display_itop_dashboard()

# =========================================================
# 7. Testing and Initialization Block (Data Seeding Tool)
# =========================================================

if __name__ == '__main__':
    # This block runs ONLY when you execute: python App.py (the fix)
    
    try:
        # Check if we are running under Streamlit (i.e., via 'streamlit run')
        if 'streamlit' in sys.modules: 
            main()
        else:
            # If not running under Streamlit, this is the data seeding execution
            db = ITopDBManager()
            
            print("--- Running FINAL Data Seeding Script (The Fix) ---")
            
            # This FIXES the blank dashboard by updating the status of the entered tickets.
            db.resolve_ticket(ticket_id=1, resolution_time_days=2.5) 
            print("Ticket 1 resolved (status: Resolved, time: 2.5).")
            
            db.resolve_ticket(ticket_id=2, resolution_time_days=1.1)
            print("Ticket 2 resolved (status: Resolved, time: 1.1).")
            
            print("\nSUCCESS! Database updated for analysis. Now, run 'streamlit run App.py'.")

    except Exception as e:
        print(f"Error during application execution: {e}")