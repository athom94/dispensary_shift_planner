import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import os

# Database file path
DB_FILE = os.path.join(os.path.dirname(__file__), "shift_planner.db")


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with all required tables and default data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT NOT NULL
        )
    """)
    
    # Create roles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    """)
    
    # Create team_members table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            role_id INTEGER,
            team_id INTEGER,
            shift_id INTEGER,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (shift_id) REFERENCES shifts(id)
        )
    """)
    
    # Create responsibilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsibilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # Create shifts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """)
    
    # Create weekly_responsibilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_responsibilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start_date TEXT NOT NULL,
            member_id INTEGER NOT NULL,
            responsibility_id INTEGER,
            FOREIGN KEY (member_id) REFERENCES team_members(id),
            FOREIGN KEY (responsibility_id) REFERENCES responsibilities(id),
            UNIQUE(week_start_date, member_id)
        )
    """)

    # Create schedules table (removed responsibility_id as it's now weekly)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            shift_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            FOREIGN KEY (shift_id) REFERENCES shifts(id),
            FOREIGN KEY (member_id) REFERENCES team_members(id),
            UNIQUE(date, shift_id, member_id)
        )
    """)
    
    # Create absences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS absences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES team_members(id)
        )
    """)
    
    # Migrate existing tables if needed (add team_id columns if they don't exist)
    try:
        cursor.execute("ALTER TABLE roles ADD COLUMN team_id INTEGER REFERENCES teams(id)")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE team_members ADD COLUMN shift_id INTEGER REFERENCES shifts(id)")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Insert default shifts if they don't exist
    shifts_data = [
        ("Early", "07:00", "15:00"),
        ("Late", "14:00", "22:00"),
        ("Day", "07:00", "17:00"),
        ("day_2", "09:00", "17:00")
    ]
    
    for shift_name, start, end in shifts_data:
        cursor.execute("""
            INSERT OR IGNORE INTO shifts (name, start_time, end_time)
            VALUES (?, ?, ?)
        """, (shift_name, start, end))
    
    conn.commit()
    conn.close()


# ==================== TEAMS ====================

def add_team(name: str, color: str, description: str = "") -> int:
    """Add a new team."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teams (name, color, description)
        VALUES (?, ?, ?)
    """, (name, color, description))
    conn.commit()
    team_id = cursor.lastrowid
    conn.close()
    return team_id


def get_all_teams() -> List[Dict]:
    """Get all teams."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY name")
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams


def get_team_by_id(team_id: int) -> Optional[Dict]:
    """Get a specific team by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_team(team_id: int, name: str, color: str, description: str = ""):
    """Update a team."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teams 
        SET name = ?, color = ?, description = ?
        WHERE id = ?
    """, (name, color, description, team_id))
    conn.commit()
    conn.close()


def delete_team(team_id: int):
    """Delete a team."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    conn.commit()
    conn.close()


def get_team_members(team_id: int) -> List[Dict]:
    """Get all members of a specific team."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tm.*, r.name as role_name, r.color as role_color
        FROM team_members tm
        LEFT JOIN roles r ON tm.role_id = r.id
        WHERE tm.team_id = ?
        ORDER BY tm.name
    """, (team_id,))
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return members


def get_team_roles(team_id: int) -> List[Dict]:
    """Get all roles within a specific team."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM roles
        WHERE team_id = ?
        ORDER BY name
    """, (team_id,))
    roles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return roles


# ==================== ROLES ====================

def add_role(name: str, color: str, team_id: Optional[int] = None) -> int:
    """Add a new role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO roles (name, color, team_id) VALUES (?, ?, ?)", (name, color, team_id))
    conn.commit()
    role_id = cursor.lastrowid
    conn.close()
    return role_id


def get_all_roles() -> List[Dict]:
    """Get all roles with team information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, t.name as team_name, t.color as team_color
        FROM roles r
        LEFT JOIN teams t ON r.team_id = t.id
        ORDER BY r.name
    """)
    roles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return roles


def update_role(role_id: int, name: str, color: str, team_id: Optional[int] = None):
    """Update a role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE roles SET name = ?, color = ?, team_id = ? WHERE id = ?", (name, color, team_id, role_id))
    conn.commit()
    conn.close()


def delete_role(role_id: int):
    """Delete a role."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    conn.close()


# ==================== TEAM MEMBERS ====================

def add_team_member(name: str, role_id: Optional[int] = None, team_id: Optional[int] = None, shift_id: Optional[int] = None) -> int:
    """Add a new team member."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO team_members (name, role_id, team_id, shift_id) VALUES (?, ?, ?, ?)", (name, role_id, team_id, shift_id))
    conn.commit()
    member_id = cursor.lastrowid
    conn.close()
    return member_id


def get_all_team_members(active_only: bool = True) -> List[Dict]:
    """Get all team members with their role and team information."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT tm.*, 
               r.name as role_name, r.color as role_color,
               t.name as team_name, t.color as team_color,
               sh.name as shift_name, sh.start_time as shift_start, sh.end_time as shift_end
        FROM team_members tm
        LEFT JOIN roles r ON tm.role_id = r.id
        LEFT JOIN teams t ON tm.team_id = t.id
        LEFT JOIN shifts sh ON tm.shift_id = sh.id
    """
    
    if active_only:
        query += " WHERE tm.active = 1"
    
    query += " ORDER BY tm.name"
    
    cursor.execute(query)
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return members


def update_team_member(member_id: int, name: str, role_id: Optional[int] = None, active: bool = True, team_id: Optional[int] = None, shift_id: Optional[int] = None):
    """Update a team member."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE team_members 
        SET name = ?, role_id = ?, active = ?, team_id = ?, shift_id = ?
        WHERE id = ?
    """, (name, role_id, active, team_id, shift_id, member_id))
    conn.commit()
    conn.close()


def delete_team_member(member_id: int):
    """Delete a team member."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()


# ==================== RESPONSIBILITIES ====================

def add_responsibility(name: str, color: str, description: str = "") -> int:
    """Add a new responsibility."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responsibilities (name, color, description)
        VALUES (?, ?, ?)
    """, (name, color, description))
    conn.commit()
    resp_id = cursor.lastrowid
    conn.close()
    return resp_id


def get_all_responsibilities() -> List[Dict]:
    """Get all responsibilities."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responsibilities ORDER BY name")
    responsibilities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return responsibilities


def update_responsibility(resp_id: int, name: str, color: str, description: str = ""):
    """Update a responsibility."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE responsibilities 
        SET name = ?, color = ?, description = ?
        WHERE id = ?
    """, (name, color, description, resp_id))
    conn.commit()
    conn.close()


def delete_responsibility(resp_id: int):
    """Delete a responsibility."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responsibilities WHERE id = ?", (resp_id,))
    conn.commit()
    conn.close()


# ==================== SHIFTS ====================

def get_all_shifts() -> List[Dict]:
    """Get all shifts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shifts ORDER BY start_time")
    shifts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return shifts


def update_shift(shift_id: int, name: str, start_time: str, end_time: str):
    """Update a shift."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE shifts 
        SET name = ?, start_time = ?, end_time = ?
        WHERE id = ?
    """, (name, start_time, end_time, shift_id))
    conn.commit()
    conn.close()


# ==================== SCHEDULES ====================

def add_schedule(date_str: str, shift_id: int, member_id: int) -> int:
    """Add a schedule entry."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO schedules (date, shift_id, member_id)
            VALUES (?, ?, ?)
        """, (date_str, shift_id, member_id))
        conn.commit()
        schedule_id = cursor.lastrowid
        conn.close()
        return schedule_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("This member is already scheduled for this shift on this date")


def get_schedules_for_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get all schedules for a date range with full details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        WITH week_start_dates AS (
            SELECT date, 
                   date(date, 'weekday 0', '-6 days') as week_start
            FROM schedules
            WHERE date BETWEEN ? AND ?
        )
        SELECT 
            s.*,
            tm.name as member_name,
            r.name as role_name,
            sh.name as shift_name,
            sh.start_time,
            sh.end_time,
            resp.name as responsibility_name,
            resp.color as responsibility_color
        FROM schedules s
        JOIN team_members tm ON s.member_id = tm.id
        LEFT JOIN roles r ON tm.role_id = r.id
        JOIN shifts sh ON s.shift_id = sh.id
        LEFT JOIN weekly_responsibilities wr ON tm.id = wr.member_id 
             AND wr.week_start_date = date(s.date, 'weekday 0', '-6 days')
        LEFT JOIN responsibilities resp ON wr.responsibility_id = resp.id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date, sh.start_time, tm.name
    """, (start_date, end_date, start_date, end_date))
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return schedules


def get_schedules_for_date(date_str: str) -> List[Dict]:
    """Get all schedules for a specific date."""
    return get_schedules_for_date_range(date_str, date_str)


def delete_schedule(schedule_id: int):
    """Delete a schedule entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()


def update_schedule_shift(schedule_id: int, new_shift_id: int):
    """Update the shift for a specific schedule entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedules 
        SET shift_id = ?
        WHERE id = ?
    """, (new_shift_id, schedule_id))
    conn.commit()
    conn.close()


def auto_populate_schedules_for_date_range(start_date: str, end_date: str) -> int:
    """
    Auto-generate schedules for active team members with default shifts.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Number of schedules created
    """
    from datetime import datetime, timedelta
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all active team members with default shifts
    cursor.execute("""
        SELECT id, shift_id 
        FROM team_members 
        WHERE active = 1 AND shift_id IS NOT NULL
    """)
    members_with_shifts = cursor.fetchall()
    
    # Get all absences for the date range
    cursor.execute("""
        SELECT member_id, start_date, end_date
        FROM absences
        WHERE start_date <= ? AND end_date >= ?
    """, (end_date, start_date))
    absences = cursor.fetchall()
    
    # Build absence map: member_id -> list of absent dates
    absence_map = {}
    for absence in absences:
        member_id = absence['member_id']
        abs_start = datetime.strptime(absence['start_date'], "%Y-%m-%d").date()
        abs_end = datetime.strptime(absence['end_date'], "%Y-%m-%d").date()
        
        if member_id not in absence_map:
            absence_map[member_id] = []
        
        # Add all dates in the absence range
        current = abs_start
        while current <= abs_end:
            absence_map[member_id].append(current)
            current += timedelta(days=1)
    
    # Generate schedules
    schedules_created = 0
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    current_date = start_dt
    while current_date <= end_dt:
        # Only schedule weekdays (Monday=0 to Friday=4)
        if current_date.weekday() < 5:
            for member in members_with_shifts:
                member_id = member['id']
                shift_id = member['shift_id']
                
                # Skip if member is absent on this date
                if member_id in absence_map and current_date in absence_map[member_id]:
                    continue
                
                # Try to insert schedule (will skip if already exists due to UNIQUE constraint)
                try:
                    cursor.execute("""
                        INSERT INTO schedules (date, shift_id, member_id)
                        VALUES (?, ?, ?)
                    """, (current_date.strftime("%Y-%m-%d"), shift_id, member_id))
                    schedules_created += 1
                except sqlite3.IntegrityError:
                    # Schedule already exists, skip
                    pass
        
        current_date += timedelta(days=1)
    
    conn.commit()
    conn.close()
    
    return schedules_created


def ensure_schedules_exist_for_date_range(start_date: str, end_date: str) -> bool:
    """
    Ensure schedules exist for the date range, auto-generating if needed.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        True if any schedules were created, False otherwise
    """
    created_count = auto_populate_schedules_for_date_range(start_date, end_date)
    return created_count > 0


# ==================== WEEKLY RESPONSIBILITIES ====================

def set_weekly_responsibility(week_start_date: str, member_id: int, responsibility_id: Optional[int]):
    """Set or update a weekly responsibility for a member."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weekly_responsibilities (week_start_date, member_id, responsibility_id)
        VALUES (?, ?, ?)
        ON CONFLICT(week_start_date, member_id) DO UPDATE SET responsibility_id = EXCLUDED.responsibility_id
    """, (week_start_date, member_id, responsibility_id))
    conn.commit()
    conn.close()


def get_weekly_responsibilities(week_start_date: str) -> List[Dict]:
    """Get all weekly responsibility assignments for a specific week."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wr.*, tm.name as member_name, resp.name as responsibility_name
        FROM weekly_responsibilities wr
        JOIN team_members tm ON wr.member_id = tm.id
        LEFT JOIN responsibilities resp ON wr.responsibility_id = resp.id
        WHERE wr.week_start_date = ?
    """, (week_start_date,))
    assignments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assignments


# ==================== ABSENCES ====================

def add_absence(member_id: int, start_date: str, end_date: str, reason: str) -> int:
    """Add an absence."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO absences (member_id, start_date, end_date, reason)
        VALUES (?, ?, ?, ?)
    """, (member_id, start_date, end_date, reason))
    conn.commit()
    absence_id = cursor.lastrowid
    conn.close()
    return absence_id


def get_all_absences() -> List[Dict]:
    """Get all absences with member information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, tm.name as member_name
        FROM absences a
        JOIN team_members tm ON a.member_id = tm.id
        ORDER BY a.start_date DESC
    """)
    absences = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return absences


def get_absences_for_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get absences that overlap with a date range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, tm.name as member_name
        FROM absences a
        JOIN team_members tm ON a.member_id = tm.id
        WHERE a.start_date <= ? AND a.end_date >= ?
        ORDER BY a.start_date
    """, (end_date, start_date))
    absences = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return absences


def update_absence(absence_id: int, start_date: str, end_date: str, reason: str):
    """Update an absence."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE absences 
        SET start_date = ?, end_date = ?, reason = ?
        WHERE id = ?
    """, (start_date, end_date, reason, absence_id))
    conn.commit()
    conn.close()


def delete_absence(absence_id: int):
    """Delete an absence."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM absences WHERE id = ?", (absence_id,))
    conn.commit()
    conn.close()


# Initialize database on import
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
