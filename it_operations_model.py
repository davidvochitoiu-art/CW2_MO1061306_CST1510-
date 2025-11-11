# it_operations_analysis.py
# --- Focus: High-Value Analysis and Insights for Service Desk Performance ---

import pandas as pd
# This line is correct, assuming ITopDBManager is defined in a separate file.
from it_operations_model import ITopDBManager 

# The analysis logic is placed back inside this function.
def get_service_desk_bottleneck_analysis():
    """
    Analyzes IT ticket data to identify bottlenecks by staff performance, 
    process status, workload, and problematic ticket categories.
    
    Returns:
        tuple: (staff_performance_df, status_bottleneck_df, workload_df, category_bottleneck_df)
    """
    
    # 1. Initialization and Data Retrieval
    # Instantiate the database manager class
    db_manager = ITopDBManager()
    
    # Fetch all ticket data as a Pandas DataFrame
    df = db_manager.read_all_tickets()
    
    if df.empty:
        # Return four Nones if no data is found
        return None, None, None, None
    
    # Ensure the key metric is numeric
    df['resolution_time_days'] = pd.to_numeric(df['resolution_time_days'], errors='coerce')
    
    # Filter for resolved tickets, as only those have a final resolution time
    resolved_df = df[df['status'] == 'Resolved'].copy()

    # =========================================================
    # TASK 1: Staff Performance Anomaly (Avg Resolution Time)
    # =========================================================
    
    # Group by 'staff_member' and calculate the MEAN resolution time.
    staff_performance_df = resolved_df.groupby('staff_member')[
        'resolution_time_days'
    ].mean().reset_index(name='Avg Resolution Time (Days)')
    
    # Sort to find the staff member with the longest average resolution time
    staff_performance_df = staff_performance_df.sort_values(
        by='Avg Resolution Time (Days)', ascending=False
    )
    
    # =========================================================
    # TASK 2: Process Inefficiency (Status Causing Delay - Volume)
    # =========================================================
    
    # Count how many tickets are currently stuck in bottleneck statuses
    bottleneck_statuses = ['Waiting for User', 'Pending Vendor', 'On Hold']
    
    status_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('status').agg(
        Tickets_Stuck=('ticket_id', 'count')
    ).reset_index()
    
    status_bottleneck_df = status_bottleneck_df.sort_values(
        by='Tickets_Stuck', ascending=False
    )
    
    # =========================================================
    # NEW TASK 3: Staff Workload (Volume Context)
    # =========================================================
    
    # Calculate the total number of tickets handled by each staff member
    staff_workload_df = resolved_df.groupby('staff_member').agg(
        Tickets_Handled=('ticket_id', 'count')
    ).reset_index().sort_values(
        by='Tickets_Handled', ascending=False
    )
    
    # Merge Workload with Performance for a comprehensive view
    staff_performance_df = staff_performance_df.merge(staff_workload_df, on='staff_member')
    
    # =========================================================
    # NEW TASK 4: Categorical Root Cause Analysis
    # =========================================================
    
    # Identify which ticket categories are most frequently getting stuck in bottleneck statuses.
    category_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('category').agg(
        Tickets_Stuck=('ticket_id', 'count')
    ).reset_index().sort_values(
        by='Tickets_Stuck', ascending=False
    )
        
    # Return all analysis results
    return staff_performance_df, status_bottleneck_df, staff_workload_df, category_bottleneck_df


if __name__ == '__main__':
    # Test block
    print("--- Running IT Operations Analysis Test ---")
    
    # NOTE: Ensure you have loaded your it_tickets.csv data first!
    staff_delay, status_delay, staff_workload, category_delay = get_service_desk_bottleneck_analysis()
    
    if staff_delay is not None:
        
        # --- TASK 1 & 3 Combined Output ---
        print("\n--- Staff Performance & Workload Ranking ---")
        print("Insight: Staff with high 'Avg Resolution Time' and low 'Tickets Handled' are likely anomalies.")
        print(staff_delay.head())
        
        # --- TASK 2 Output ---
        print("\n--- Status Bottlenecks (Tickets Stuck) ---")
        print("Insight: Focus on automating follow-ups for the highest volume status.")
        print(status_delay)
        
        # --- NEW TASK 4 Output ---
        print("\n--- Categorical Bottlenecks (Problem Areas) ---")
        print("Insight: The top category suggests where to focus long-term process improvement (e.g., knowledge base, automation).")
        print(category_delay.head())

    else:
        print("Analysis failed. Database table is likely empty.")