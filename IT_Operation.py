# it_operations_analysis.py
# --- Focus: High-Value Analysis and Insights for Service Desk Performance ---

import pandas as pd
from it_operations_model import ITopDBManager

def get_service_desk_bottleneck_analysis():
    """
    Analyzes IT ticket data to identify bottlenecks by staff performance and 
    process status (e.g., 'Waiting for User').
    """
    
    db_manager = ITopDBManager()
    
    # 1. R (Read): Fetch all ticket data as a Pandas DataFrame
    df = db_manager.read_all_tickets()
    
    if df.empty:
        return None, None
    
    # Ensure the key metric is numeric
    df['resolution_time_days'] = pd.to_numeric(df['resolution_time_days'], errors='coerce')
    
    # =========================================================
    # TASK 1: Staff Performance Anomaly (Staff Causing Delay)
    # =========================================================
    
    # Filter for resolved tickets, as only those have a final resolution time
    resolved_df = df[df['status'] == 'Resolved'].copy()
    
    # TODO: Group by 'staff_member' and calculate the MEAN resolution time.
    staff_performance_df = resolved_df.groupby('staff_member')[
        'resolution_time_days'
    ].mean().reset_index(name='Avg Resolution Time (Days)')
    
    # Sort to find the staff member with the longest average resolution time
    staff_performance_df = staff_performance_df.sort_values(
        by='Avg Resolution Time (Days)', ascending=False
    )
    
    # =========================================================
    # TASK 2: Process Inefficiency (Status Causing Delay)
    # =========================================================
    
    # Count how many tickets are currently stuck in bottleneck statuses
    bottleneck_statuses = ['Waiting for User', 'Pending Vendor', 'On Hold']
    
    status_bottleneck_df = df[df['status'].isin(bottleneck_statuses)].groupby('status').agg(
        Tickets_Stuck=('ticket_id', 'count')
    ).reset_index()
    
    status_bottleneck_df = status_bottleneck_df.sort_values(
        by='Tickets_Stuck', ascending=False
    )
        
    # Return both results
    return staff_performance_df, status_bottleneck_df


if __name__ == '__main__':
    # Test block
    print("--- Running IT Operations Analysis Test ---")
    
    # NOTE: Ensure you have loaded your it_tickets.csv data first!
    staff_delay, status_delay = get_service_desk_bottleneck_analysis()
    
    if staff_delay is not None:
        print("\n--- Staff Performance Ranking (Longest Resolution Time) ---")
        print(staff_delay.head())
        
        print("\n--- Status Bottlenecks (Tickets Stuck) ---")
        print(status_delay)
    else:
        print("Analysis failed. Database table is likely empty.")