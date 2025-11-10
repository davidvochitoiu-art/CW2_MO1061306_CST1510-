# Cyber Security Module
# ---  Domain Focus: Cybersecurity ---
# Manages Cyber_incidents" table and implements CRUd Operations for cybersecurity incidents.

import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. Entity class (OOP refactoring)
# ==========================================


class CyberDBManager:
    """
    Handles all secure database connections and parameterized queries 
    for the cyber_incidents table.
    """

    def __init__(self, db_path="intelligence_platform.db"):
        # The database file must be the same for all three domains
        self.db_path = db_path
        self.create_table() # Ensure the table exists on initialization)

        