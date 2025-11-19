import sqlite3

def connect_db(db_name):
    """Connect to the SQLite database."""
    conn = sqlite3.connect(db_name)
    return conn

def create_table(conn): #incident_id,timestamp,severity,category,status,description
    """Create a table for storing cyber security incidents."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id INTEGER PRIMARY KEY,
            timestamp DateTime NOT NULL,
            severity TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()

def add_incident(conn, incident_id, timestamp, severity, category, status, description):
    """Add a new cyber security incident to the database."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (incident_id,timestamp,severity,category,status,description)
        VALUES (?, \'?\', \'?\', \'?\', \'?\', \'?\')
    ''', (incident_id,timestamp,severity,category,status,description))
    conn.commit()

def get_incidents(conn):
    """Retrieve all cyber security incidents from the database."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents')
    return cursor.fetchall()

def import_incidents_from_file(conn, file_path):
    """Import cyber security incidents from a text file."""
    with open(file_path, 'r') as file:
        for line in file:
            incident_id,timestamp,severity,category,status,description = line.strip().split(',')
            add_incident(conn, incident_id,timestamp,severity,category,status,description)

if __name__ == "__main__":
    db_connection = connect_db('cyber_security.db')
    create_table(db_connection)
    # Example usage:
    #add_incident(db_connection, 1, '2024-06-01T12:00:00', 'High', 'Phishing', 'Open', 'User received a phishing email.')
    #incidents = get_incidents(db_connection)
    #for incident in incidents:
    #    print(incident)
    # Import incidents from a file
    import_incidents_from_file(db_connection, "DATA\\cyber_incidents.csv")
    db_connection.close()

    