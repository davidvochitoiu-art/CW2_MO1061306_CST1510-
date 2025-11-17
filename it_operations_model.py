# it_operations_model.py
# COMBINED FILE: Contains Entity, DB Manager, and Analysis Logic.

import sqlite3
import pandas as pd

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
# 2. ITopDBManager Class 
# =========================================================

class ITopDBManager:
    """
    Manages the SQLite connection and CRUD operations for the IT tickets table.
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
    """
    Analyzes IT ticket data to identify bottlenecks by staff performance, 
    process status, workload, and problematic ticket categories.
    """
    db_manager = ITopDBManager()
    df = db_manager.read_all_tickets()
    
    if df.empty:
        return None, None, None, None
    
    df['resolution_time_days'] = pd.to_numeric(df['resolution_time_days'], errors='coerce')
    resolved_df = df[df['status'] == 'Resolved'].copy()

    # Staff Performance Anomaly (Avg Resolution Time)
    staff_performance_df = resolved_df.groupby('staff_member')[
        'resolution_time_days'
    ].mean().reset_index(name='Avg Resolution Time (Days)').sort_values(
        by='Avg Resolution Time (Days)', ascending=False
    )
    
    # Process Inefficiency (Status Causing Delay - Volume)
    bottleneck_statuses = ['Waiting for User', 'Pending Vendor', 'On Hold']
    
    status_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('status').agg(
        Tickets_Stuck=('ticket_id', 'count')
    ).reset_index().sort_values(
        by='Tickets_Stuck', ascending=False
    )
    
    # Staff Workload and Merge
    staff_workload_df = resolved_df.groupby('staff_member').agg(
        Tickets_Handled=('ticket_id', 'count')
    ).reset_index()
    
    staff_performance_df = staff_performance_df.merge(staff_workload_df, on='staff_member')
    
    # Categorical Root Cause Analysis
    category_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('category').agg(
        Tickets_Stuck=('ticket_id', 'count')
    ).reset_index().sort_values(
        by='Tickets_Stuck', ascending=False
    )
        
    return staff_performance_df, status_bottleneck_df, staff_workload_df, category_bottleneck_df


# =========================================================
# 4. Main Execution Block
# =========================================================

if __name__ == '__main__':
    print("--- Running IT Operations Analysis Test ---")
    
    staff_delay, status_delay, staff_workload, category_delay = get_service_desk_bottleneck_analysis()
    
    if staff_delay is not None:
        print("\n--- Staff Performance & Workload Ranking ---")
        print(staff_delay.head())
        print("\n--- Status Bottlenecks (Tickets Stuck) ---")
        print(status_delay)
        print("\n--- Categorical Bottlenecks (Problem Areas) ---")
        print(category_delay.head())
    else:
        print("Analysis failed. Database table 'it_tickets' is likely empty.")
        