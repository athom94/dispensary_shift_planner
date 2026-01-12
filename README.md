# Shift Planner App 📅

A Streamlit-based shift planning application for managing team schedules, roles, responsibilities, and absences.

## Features

- **Team Management**: Add and manage team members with roles
- **Shift Types**: 
  - Early (7am-3pm)
  - Late (2pm-10pm)
  - Day (7am-5pm)
- **Responsibility Tracking**: Assign primary responsibilities to shifts
- **Holiday Management**: Track absences and holidays
- **Visual Schedule**: Daily Gantt chart with color-coded responsibilities
- **Full CRUD Operations**: All data can be added, edited, and deleted through the app

## Installation

1. Make sure you have Python installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```

The app will open in your default web browser.

## Navigation

- **Dashboard**: View daily schedules with Gantt chart visualization
- **Schedule**: Add and manage shift assignments
- **Team Members**: Manage your team
- **Roles**: Define and manage team roles
- **Responsibilities**: Define primary responsibilities
- **Absences**: Track holidays and absences

## Database

The app uses SQLite (`shift_planner.db`) to store all data locally. The database is automatically created on first run.

## Tips

1. Start by adding roles and responsibilities
2. Add team members and assign them roles
3. Use the Schedule page to assign shifts
4. View the Dashboard to see the daily Gantt chart
5. Add absences/holidays as needed
