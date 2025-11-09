# Cyber Security Module
# ---  Domain Focus: Cybersecurity ---
# Manages Cyber_incidents" table and implements CRUd Operations for cybersecurity incidents.

import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. Entity class (OOP refactoring)
# ==========================================
class SecurityIncident:
    """Represents a cybersecurity incident entity."""

    def__intit __

    #Attribute mirror the required columns in the database tables
    def __init__(self, incident_id, incident_type, description, reporte