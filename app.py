import streamlit as st
from datetime import datetime, timedelta, date
import database as db
import gantt_view
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Shift Planner",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# Custom CSS for modern styling
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
/* Global Styles */
* {
    font-family: 'Outfit', sans-serif !important;
}

.main {
    background-color: #0e1117;
    color: #e0e0e0;
}

/* Header Styling */
.main-header {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding: 2rem 0;
    letter-spacing: -0.05em;
}

/* Glassmorphism Containers */
.glass-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    color: #f0f0f0;
}

/* Ensure metric-container matches for backwards compatibility if needed */
.metric-container {
    padding: 0.5rem;
}

/* Card/Section Styling */
.stExpander {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
}

.stExpander summary {
    color: #f0f0f0 !important;
}

/* Hide internal widget keys in expanders */
.stExpander summary::before {
    content: none !important;
}

.stExpander [data-testid] {
    color: transparent !important;
}

/* Buttons */
.stButton>button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    border: none !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 0.6rem 1rem !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0b0d11 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #00f2fe !important;
}

[data-testid="stMetricLabel"] {
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.8rem !important;
    color: #b0b0b0 !important;
}

/* Success/Warning Boxes */
.success-box {
    padding: 1rem;
    border-radius: 12px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.warning-box {
    padding: 1rem;
    border-radius: 12px;
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.2);
    color: #f59e0b;
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent !important;
    border-radius: 4px 4px 0 0;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
    font-weight: 600;
    color: #b0b0b0;
}

.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #00f2fe !important;
}

/* Input and Select Styling */
stTextInput, stSelectbox, stTextArea {
    color: #f0f0f0 !important;
}

/* General text readability */
p, span, div {
    color: #e0e0e0;
}

label {
    color: #d0d0d0 !important;
}
</style>
""")


# ==================== UI HELPERS ====================

def get_options_dict(items, include_none=False, none_label="None", name_field='name', id_field='id', format_func=None):
    """Helper to create dictionary for selectbox options."""
    options = {}
    if include_none:
        options[none_label] = None
    
    for item in items:
        label = format_func(item) if format_func else item[name_field]
        options[label] = item[id_field]
    return options


def render_save_delete_buttons(id, on_save, on_delete, save_label="💾 Save Changes", delete_label="🗑️ Delete"):
    """Standardized save and delete buttons."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button(save_label, key=f"save_{id}", type="primary"):
            on_save()
    with col2:
        if st.button(delete_label, key=f"del_{id}"):
            on_delete()


def render_card(title=None, subtitle=None):
    """Context manager-like helper to render content inside a glass card."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"_{subtitle}_")
    # Content goes here via normal Streamlit calls
    # Need to remember to close it manually or use a trick.
    # Since Streamlit doesn't support context managers for custom HTML easily, 
    # we'll just provide a helper that returns the closing tag or just use it as markers.
    pass

def card_begin(title=None):
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f"#### {title}")

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main application entry point."""
    db.init_db()
    
    # Sidebar navigation
    st.sidebar.title("📅 Shift Planner")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Teams", "Schedule", "Team Members", "Roles", "Responsibilities", "Absences"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: Use the Dashboard to view daily schedules and the Schedule page to assign shifts.")
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Teams":
        show_teams_page()
    elif page == "Schedule":
        show_schedule_page()
    elif page == "Team Members":
        show_team_members_page()
    elif page == "Roles":
        show_roles_page()
    elif page == "Responsibilities":
        show_responsibilities_page()
    elif page == "Absences":
        show_absences_page()


def get_week_dates(reference_date):
    """Get Monday-Friday dates for the week containing reference_date."""
    # Find Monday of the week
    days_since_monday = reference_date.weekday()
    monday = reference_date - timedelta(days=days_since_monday)
    
    # Generate Mon-Fri
    week_dates = [monday + timedelta(days=i) for i in range(5)]
    return week_dates


def show_dashboard():
    """Dashboard page with weekly Gantt view (Mon-Fri)."""
    st.markdown('<div class="main-header">📊 Weekly Dashboard</div>', unsafe_allow_html=True)
    
    # Initialize week offset in session state
    if 'week_offset' not in st.session_state:
        st.session_state.week_offset = 0
    
    # Week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous Week", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    
    with col2:
        if st.button("📅 This Week", use_container_width=True):
            st.session_state.week_offset = 0
            st.rerun()
    
    with col3:
        if st.button("Next Week ➡️", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()
    
    # Calculate the reference date based on week offset
    reference_date = date.today() + timedelta(weeks=st.session_state.week_offset)
    week_dates = get_week_dates(reference_date)
    
    # Display week range
    st.markdown(f"### Week of {week_dates[0].strftime('%B %d')} - {week_dates[4].strftime('%B %d, %Y')}")
    
    # Get week date range
    week_start = week_dates[0].strftime("%Y-%m-%d")
    week_end = week_dates[4].strftime("%Y-%m-%d")
    
    # Team filter
    teams = db.get_all_teams()
    team_options = get_options_dict(teams, include_none=True, none_label="All Teams")
    
    selected_team_name = st.selectbox(
        "Filter by Team:",
        options=list(team_options.keys()),
        key="dashboard_team_filter"
    )
    selected_team_id = team_options[selected_team_name]
    
    st.markdown("---")
    
    # Get all schedules and absences for the week
    week_start = week_dates[0].strftime("%Y-%m-%d")
    week_end = week_dates[4].strftime("%Y-%m-%d")
    all_schedules = db.get_schedules_for_date_range(week_start, week_end)
    all_absences = db.get_absences_for_date_range(week_start, week_end)
    
    # Filter by team if selected
    if selected_team_id is not None:
        # Get team members for the selected team
        team_members = db.get_team_members(selected_team_id)
        team_member_ids = [m['id'] for m in team_members]
        
        # Filter schedules and absences to only include team members
        all_schedules = [s for s in all_schedules if s['member_id'] in team_member_ids]
        all_absences = [a for a in all_absences if a['member_id'] in team_member_ids]
    
    # Show weekly summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Total Shifts", len(all_schedules)),
        ("Active Members", len(set(s['member_id'] for s in all_schedules))),
        ("Absences", len(all_absences)),
        ("Unassigned", sum(1 for s in all_schedules if not s.get('responsibility_name')))
    ]
    
    for col, (label, value) in zip([col1, col2, col3, col4], metrics):
        with col:
            card_begin()
            st.metric(label, value)
            card_end()
    
    st.markdown("---")
    
    # Show warnings for scheduled members who are absent
    if all_schedules and all_absences:
        # Build a map of member_id to dates they're absent
        absent_dates = {}
        for absence in all_absences:
            member_id = absence['member_id']
            start = datetime.strptime(absence['start_date'], "%Y-%m-%d").date()
            end = datetime.strptime(absence['end_date'], "%Y-%m-%d").date()
            
            if member_id not in absent_dates:
                absent_dates[member_id] = []
            
            # Add all dates in the absence range
            current = start
            while current <= end:
                absent_dates[member_id].append(current)
                current += timedelta(days=1)
        
        # Check for conflicts
        conflicts = []
        for schedule in all_schedules:
            schedule_date = datetime.strptime(schedule['date'], "%Y-%m-%d").date()
            member_id = schedule['member_id']
            
            if member_id in absent_dates and schedule_date in absent_dates[member_id]:
                conflicts.append(f"{schedule['member_name']} on {schedule['date']}")
        
        if conflicts:
            st.warning(f"⚠️ **Scheduling Conflicts Detected:**\n\n" + "\n".join([f"- {c}" for c in conflicts]))
            st.markdown("---")
    
    # Display 5 Gantt charts (Monday - Friday)
    for day_date in week_dates:
        date_str = day_date.strftime("%Y-%m-%d")
        day_name = day_date.strftime("%A, %B %d")
        
        # Filter schedules and absences for this day
        day_schedules = [s for s in all_schedules if s['date'] == date_str]
        day_absences = [a for a in all_absences 
                       if datetime.strptime(a['start_date'], "%Y-%m-%d").date() <= day_date 
                       and datetime.strptime(a['end_date'], "%Y-%m-%d").date() >= day_date]
        
        # Create expander for each day
        st.markdown("")  # Add spacing
        with st.expander(f"{day_name} - {len(day_schedules)} shift(s)", expanded=True):
            if day_schedules or day_absences:
                fig = gantt_view.create_daily_gantt(day_schedules, day_absences, date_str)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show brief summary
                if day_schedules:
                    summary_text = f"**Scheduled:** "
                    member_shifts = {}
                    for s in day_schedules:
                        name = s['member_name']
                        if name not in member_shifts:
                            member_shifts[name] = []
                        member_shifts[name].append(s['shift_name'])
                    
                    summary_text += ", ".join([f"{name} ({', '.join(shifts)})" for name, shifts in member_shifts.items()])
                    st.markdown(summary_text)
                
                if day_absences:
                    absent_members = [a['member_name'] for a in day_absences]
                    st.markdown(f"**Absent:** {', '.join(absent_members)}")
            else:
                st.info("No schedules or absences for this day.")


def show_teams_page():
    """Teams management page."""
    st.markdown('<div class="main-header">👥 Teams</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Team", "📋 View/Edit Teams"])
    
    with tab1:
        card_begin("Add New Team")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_name = st.text_input("Team Name")
            team_desc = st.text_area("Description (Optional)")
        with col2:
            team_color = st.color_picker("Color", value="#2ecc71")
        
        if st.button("Add Team", type="primary"):
            if team_name:
                try:
                    db.add_team(team_name, team_color, team_desc)
                    st.success(f"✅ Added team: {team_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please enter a team name.")
        card_end()
    
    with tab2:
        st.subheader("All Teams")
        
        teams = db.get_all_teams()
        
        if teams:
            for team in teams:
                # Get member and role counts for this team
                team_members = db.get_team_members(team['id'])
                team_roles = db.get_team_roles(team['id'])
                
                with st.expander(f"**{team['name']}** ({len(team_members)} members, {len(team_roles)} roles)", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Team Name", value=team['name'], key=f"team_name_{team['id']}")
                        new_desc = st.text_area("Description", value=team.get('description', ''), key=f"team_desc_{team['id']}")
                    
                    with col2:
                        new_color = st.color_picker("Color", value=team['color'], key=f"team_color_{team['id']}")
                    
                    # Show team members and roles
                    if team_members:
                        st.markdown("**Members:**")
                        member_names = [m['name'] for m in team_members]
                        st.markdown(", ".join(member_names))
                    
                    if team_roles:
                        st.markdown("**Roles:**")
                        role_names = [r['name'] for r in team_roles]
                        st.markdown(", ".join(role_names))
                    
                    def save_team():
                        try:
                            db.update_team(team['id'], new_name, new_color, new_desc)
                            st.success("Updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    def delete_team():
                        try:
                            db.delete_team(team['id'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Cannot delete: {str(e)}")
                            
                    render_save_delete_buttons(team['id'], save_team, delete_team)
        else:
            st.info("No teams found.")


def show_schedule_page():
    """Schedule management page with weekly scheduling."""
    st.markdown('<div class="main-header">📅 Schedule Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Weekly Schedule", "📋 View/Edit Schedules"])
    
    with tab1:
        card_begin("Add Schedule for the Week")
        st.info("💡 Schedules are automatically populated based on each member's default shift. Use this page to add one-off schedules or override defaults.")
        
        # Get data for dropdowns
        members = db.get_all_team_members()
        shifts = db.get_all_shifts()
        responsibilities = db.get_all_responsibilities()
        
        if not members:
            st.warning("⚠️ No team members found. Please add team members first.")
            card_end()
            return
        
        # Week selector
        col1, col2 = st.columns(2)
        with col1:
            selected_week_start = st.date_input(
                "Week Starting (Monday)", 
                value=date.today() - timedelta(days=date.today().weekday()),
                key="week_start"
            )
        
        # Calculate the week dates
        week_dates = get_week_dates(selected_week_start)
        
        with col2:
            st.info(f"Week: {week_dates[0].strftime('%b %d')} - {week_dates[4].strftime('%b %d, %Y')}")
        
        # Get absences for this week
        week_start_str = week_dates[0].strftime("%Y-%m-%d")
        week_end_str = week_dates[4].strftime("%Y-%m-%d")
        week_absences = db.get_absences_for_date_range(week_start_str, week_end_str)
        
        # Build absence lookup
        absence_map = {}  # member_id -> list of dates
        for absence in week_absences:
            member_id = absence['member_id']
            start = datetime.strptime(absence['start_date'], "%Y-%m-%d").date()
            end = datetime.strptime(absence['end_date'], "%Y-%m-%d").date()
            
            if member_id not in absence_map:
                absence_map[member_id] = []
            
            current = start
            while current <= end:
                absence_map[member_id].append(current)
                current += timedelta(days=1)
        
        st.markdown("---")
        st.markdown("### Bulk Actions")
        
        if st.button("🚀 Populate Week with Default Shifts", help="Adds default shifts for all active members who have one, for the selected Monday-Friday."):
            active_members = [m for m in members if m['active'] and m['shift_id']]
            if not active_members:
                st.warning("No active members with default shifts found.")
            else:
                success_count = 0
                error_count = 0
                already_scheduled = 0
                
                # Check for absences before scheduling
                # absence_map is already built above
                
                for member in active_members:
                    for day_date in week_dates:
                        # Skip if absent
                        if member['id'] in absence_map and day_date in absence_map[member['id']]:
                            continue
                            
                        try:
                            db.add_schedule(
                                day_date.strftime("%Y-%m-%d"),
                                member['shift_id'],
                                member['id']
                            )
                            success_count += 1
                        except ValueError:
                            already_scheduled += 1
                        except Exception:
                            error_count += 1
                
                if success_count > 0:
                    st.success(f"✅ Added {success_count} shifts successfully!")
                if already_scheduled > 0:
                    st.info(f"ℹ️ {already_scheduled} shifts were already scheduled and skipped.")
                if error_count > 0:
                    st.error(f"❌ {error_count} shifts failed to be added.")
                    
                if success_count > 0:
                    st.rerun()

        st.markdown("---")
        st.markdown("### Quick Add Schedule")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            member_options = get_options_dict(members)
            selected_member_name = st.selectbox("Team Member", options=list(member_options.keys()), key="quick_member")
            selected_member_id = member_options[selected_member_name]
        
        with col2:
            shift_options = get_options_dict(shifts, format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
            
            # Find default shift index for selected member
            default_shift_id = next((m['shift_id'] for m in members if m['id'] == selected_member_id), None)
            default_shift_name = next((name for name, id in shift_options.items() if id == default_shift_id), list(shift_options.keys())[0] if shift_options else None)
            
            selected_shift_name = st.selectbox(
                "Shift", 
                options=list(shift_options.keys()), 
                index=list(shift_options.keys()).index(default_shift_name) if default_shift_name in shift_options else 0,
                key="quick_shift"
            )
            selected_shift_id = shift_options[selected_shift_name]
        
        with col3:
            st.info("💡 Responsibility is assigned weekly in the 'View/Edit' tab.")
        
        # Day selection
        st.markdown("**Select Days:**")
        day_cols = st.columns(5)
        selected_days = []
        
        for idx, (day_date, col) in enumerate(zip(week_dates, day_cols)):
            with col:
                day_name = day_date.strftime("%a %m/%d")
                
                # Check if member is absent on this day
                is_absent = selected_member_id in absence_map and day_date in absence_map[selected_member_id]
                
                if is_absent:
                    st.warning(f"🏖️ {day_name}")
                    checkbox_label = f"{day_name} (ABSENT)"
                else:
                    checkbox_label = day_name
                
                if st.checkbox(checkbox_label, key=f"day_{idx}", disabled=is_absent):
                    selected_days.append(day_date)
        
        if st.button("Add Schedule for Selected Days", type="primary"):
            if not selected_days:
                st.error("Please select at least one day.")
            else:
                success_count = 0
                error_messages = []
                
                for day_date in selected_days:
                    try:
                        db.add_schedule(
                            day_date.strftime("%Y-%m-%d"),
                            selected_shift_id,
                            selected_member_id
                        )
                        success_count += 1
                    except ValueError as e:
                        error_messages.append(f"{day_date.strftime('%a %m/%d')}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"✅ Added {success_count} schedule(s) successfully!")
                
                if error_messages:
                    st.error("❌ Some schedules could not be added:\n" + "\n".join(error_messages))
                
                if success_count > 0:
                    st.rerun()
        card_end()
    
    with tab2:
        st.subheader("View and Edit Schedules")
        
        # View mode selector
        view_mode = st.radio("View by:", ["By Person", "By Date"], horizontal=True, key="view_mode")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today(), key="view_start")
        with col2:
            end_date = st.date_input("End Date", value=date.today() + timedelta(days=6), key="view_end")
        
        # Don't auto-populate in edit view - only show what's actually scheduled
        # (Auto-population happens in the "Add Weekly Schedule" tab)
        
        schedules = db.get_schedules_for_date_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        # --- Weekly Responsibilities Section ---
        st.markdown("---")
        st.subheader("📋 Weekly Responsibility Assignments")
        st.markdown("Assign a responsibility to each member for the entire week.")
        
        # Get Monday of the week for the selected start_date
        monday = start_date - timedelta(days=start_date.weekday())
        monday_str = monday.strftime("%Y-%m-%d")
        
        st.info(f"Setting responsibilities for week of: **{monday.strftime('%B %d, %Y')}**")
        
        active_members = db.get_all_team_members(active_only=True)
        weekly_assignments = db.get_weekly_responsibilities(monday_str)
        weekly_map = {a['member_id']: a['responsibility_id'] for a in weekly_assignments}
        
        responsibilities = db.get_all_responsibilities()
        resp_options = get_options_dict(responsibilities, include_none=True, none_label="Unassigned")
        
        # Use a form for bulk updates
        with st.form("weekly_resp_form"):
            for member in active_members:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**{member['name']}**")
                with col2:
                    current_resp_id = weekly_map.get(member['id'])
                    current_resp_name = next((name for name, id in resp_options.items() if id == current_resp_id), "Unassigned")
                    
                    new_resp_name = st.selectbox(
                        f"Responsibility for {member['name']}",
                        options=list(resp_options.keys()),
                        index=list(resp_options.keys()).index(current_resp_name),
                        key=f"weekly_resp_{member['id']}",
                        label_visibility="collapsed"
                    )
                
            if st.form_submit_button("💾 Save Weekly Responsibilities", type="primary", use_container_width=True):
                for member in active_members:
                    val = st.session_state[f"weekly_resp_{member['id']}"]
                    db.set_weekly_responsibility(monday_str, member['id'], resp_options[val])
                st.success("Weekly responsibilities updated!")
                st.rerun()
        
        # --- Daily Shifts Section ---
        st.markdown("---")
        st.subheader("📅 Daily Shifts (Times)")
        
        if schedules:
            if view_mode == "By Date":
                # Group by date
                schedules_by_date = {}
                for schedule in schedules:
                    date_key = schedule['date']
                    if date_key not in schedules_by_date:
                        schedules_by_date[date_key] = []
                    schedules_by_date[date_key].append(schedule)
                
                # Display grouped by date
                for date_key in sorted(schedules_by_date.keys()):
                    day_date = datetime.strptime(date_key, "%Y-%m-%d").date()
                    day_name = day_date.strftime("%A, %B %d, %Y")
                    
                    with st.expander(f"**{day_name}** - {len(schedules_by_date[date_key])} shifts", expanded=False):
                        for schedule in schedules_by_date[date_key]:
                            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 2, 1.5, 0.8])
                            
                            with col1:
                                st.text(schedule['member_name'])
                            
                            with col2:
                                # Get all shifts
                                shifts = db.get_all_shifts()
                                shift_options = get_options_dict(shifts, format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
                                
                                current_shift_name = f"{schedule['shift_name']} ({schedule['start_time']}-{schedule['end_time']})"
                                current_index = list(shift_options.keys()).index(current_shift_name) if current_shift_name in shift_options else 0
                                
                                new_shift_name = st.selectbox(
                                    "Shift",
                                    options=list(shift_options.keys()),
                                    index=current_index,
                                    key=f"shift_{schedule['id']}",
                                    label_visibility="collapsed"
                                )
                                
                                # Check if changed and update
                                new_shift_id = shift_options[new_shift_name]
                                if new_shift_id != schedule['shift_id']:
                                    if st.button("✓", key=f"update_{schedule['id']}", help="Apply change"):
                                        db.update_schedule_shift(schedule['id'], new_shift_id)
                                        st.rerun()
                            
                            with col3:
                                # Show responsibility (read-only from weekly)
                                resp_name = schedule.get('responsibility_name', 'Unassigned')
                                resp_color = schedule.get('responsibility_color', '#cccccc')
                                st.markdown(f'<span style="background-color: {resp_color}; color: white; padding: 2px 6px; border-radius: 4px;">{resp_name}</span>', unsafe_allow_html=True)
                            
                            with col4:
                                st.text(f"{schedule['start_time']}-{schedule['end_time']}")
                            
                            with col5:
                                if st.button("🗑️", key=f"del_{schedule['id']}", help="Delete shift"):
                                    db.delete_schedule(schedule['id'])
                                    st.rerun()
            
            else:  # By Person view
                # Group by person
                schedules_by_person = {}
                for schedule in schedules:
                    member_key = schedule['member_id']
                    if member_key not in schedules_by_person:
                        schedules_by_person[member_key] = {
                            'name': schedule['member_name'],
                            'shifts': []
                        }
                    schedules_by_person[member_key]['shifts'].append(schedule)
                
                # Display grouped by person
                for member_id, member_data in sorted(schedules_by_person.items(), key=lambda x: x[1]['name']):
                    shifts = sorted(member_data['shifts'], key=lambda x: x['date'])
                    
                    with st.expander(f"**{member_data['name']}** - {len(shifts)} shifts", expanded=False):
                        st.markdown("#### Schedule Overview")
                        
                        for schedule in shifts:
                            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 2, 1.5, 0.8])
                            
                            with col1:
                                day_date = datetime.strptime(schedule['date'], "%Y-%m-%d").date()
                                st.text(day_date.strftime("%a, %b %d"))
                            
                            with col2:
                                # Get all shifts
                                shifts_list = db.get_all_shifts()
                                shift_options = get_options_dict(shifts_list, format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
                                
                                current_shift_name = f"{schedule['shift_name']} ({schedule['start_time']}-{schedule['end_time']})"
                                current_index = list(shift_options.keys()).index(current_shift_name) if current_shift_name in shift_options else 0
                                
                                new_shift_name = st.selectbox(
                                    "Shift",
                                    options=list(shift_options.keys()),
                                    index=current_index,
                                    key=f"shift_{schedule['id']}",
                                    label_visibility="collapsed"
                                )
                                
                                # Check if changed and show apply button
                                new_shift_id = shift_options[new_shift_name]
                                if new_shift_id != schedule['shift_id']:
                                    if st.button("✓", key=f"update_{schedule['id']}", help="Apply change"):
                                        db.update_schedule_shift(schedule['id'], new_shift_id)
                                        st.rerun()
                            
                            with col3:
                                # Show responsibility (read-only from weekly)
                                resp_name = schedule.get('responsibility_name', 'Unassigned')
                                resp_color = schedule.get('responsibility_color', '#cccccc')
                                st.markdown(f'<span style="background-color: {resp_color}; color: white; padding: 2px 6px; border-radius: 4px;">{resp_name}</span>', unsafe_allow_html=True)
                            
                            with col4:
                                st.text(f"{schedule['start_time']}-{schedule['end_time']}")
                            
                            with col5:
                                if st.button("🗑️", key=f"del_{schedule['id']}", help="Delete shift"):
                                    db.delete_schedule(schedule['id'])
                                    st.rerun()
                        
                        # Bulk actions for this person
                        st.markdown("---")
                        st.markdown("**Bulk Actions:**")
                        
                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            # Apply same shift to all days
                            shifts_list = db.get_all_shifts()
                            shift_options = get_options_dict(shifts_list, format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
                            
                            bulk_shift = st.selectbox(
                                "Apply shift to all days:",
                                options=list(shift_options.keys()),
                                key=f"bulk_shift_{member_id}"
                            )
                            
                            if st.button("Apply to All", key=f"bulk_apply_{member_id}", type="secondary"):
                                bulk_shift_id = shift_options[bulk_shift]
                                for schedule in shifts:
                                    db.update_schedule_shift(schedule['id'], bulk_shift_id)
                                st.success(f"Applied {bulk_shift} to all days!")
                                st.rerun()
                        
                        with bcol2:
                            if st.button("Delete All Shifts", key=f"bulk_delete_{member_id}", type="secondary"):
                                for schedule in shifts:
                                    db.delete_schedule(schedule['id'])
                                st.success(f"Deleted all shifts for {member_data['name']}")
                                st.rerun()
        else:
            st.info("No schedules found for the selected date range.")


def show_team_members_page():
    """Team members management page."""
    st.markdown('<div class="main-header">👥 Team Members</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Member", "📋 View/Edit Members"])
    
    with tab1:
        card_begin("Add New Team Member")
        roles = db.get_all_roles()
        teams = db.get_all_teams()
        
        member_name = st.text_input("Name")
        
        col1, col2 = st.columns(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_options = get_options_dict(teams, include_none=True, none_label="No Team")
            selected_team_name = st.selectbox("Team", options=list(team_options.keys()))
            selected_team_id = team_options[selected_team_name]
        
        with col2:
            role_options = get_options_dict(roles, include_none=True, none_label="No Role")
            selected_role_name = st.selectbox("Role", options=list(role_options.keys()))
            selected_role_id = role_options[selected_role_name]
            
            shifts = db.get_all_shifts()
            shift_options = get_options_dict(shifts, include_none=True, none_label="No Default Shift", 
                                           format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
            selected_shift_name = st.selectbox("Default Shift", options=list(shift_options.keys()))
            selected_shift_id = shift_options[selected_shift_name]
        
        if st.button("Add Team Member", type="primary"):
            if member_name:
                try:
                    db.add_team_member(member_name, selected_role_id, selected_team_id, selected_shift_id)
                    st.success(f"✅ Added {member_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please enter a name.")
        card_end()
    
    with tab2:
        st.subheader("Team Members")
        
        members = db.get_all_team_members(active_only=False)
        
        if members:
            for member in members:
                team_badge = f" [{member.get('team_name', 'No Team')}]" if member.get('team_name') else ""
                with st.expander(f"{'✓' if member['active'] else '✗'} {member['name']} - {member.get('role_name', 'No Role')}{team_badge}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Name", value=member['name'], key=f"name_{member['id']}")
                        
                        teams = db.get_all_teams()
                        team_options = get_options_dict(teams, include_none=True, none_label="No Team")
                        
                        current_team = member.get('team_name', 'No Team')
                        new_team_name = st.selectbox(
                            "Team",
                            options=list(team_options.keys()),
                            index=list(team_options.keys()).index(current_team) if current_team in team_options else 0,
                            key=f"team_{member['id']}"
                        )
                        new_team_id = team_options[new_team_name]
                        
                        roles = db.get_all_roles()
                        role_options = get_options_dict(roles, include_none=True, none_label="No Role")
                        
                        current_role = member.get('role_name', 'No Role')
                        new_role_name = st.selectbox(
                            "Role",
                            options=list(role_options.keys()),
                            index=list(role_options.keys()).index(current_role) if current_role in role_options else 0,
                            key=f"role_{member['id']}"
                        )
                        new_role_id = role_options[new_role_name]
                    
                    with col2:
                        new_active = st.checkbox("Active", value=bool(member['active']), key=f"active_{member['id']}")
                        
                        shifts = db.get_all_shifts()
                        shift_options = get_options_dict(shifts, include_none=True, none_label="No Default Shift",
                                                       format_func=lambda s: f"{s['name']} ({s['start_time']}-{s['end_time']})")
                        
                        current_shift_name = next((name for name, id in shift_options.items() if id == member['shift_id']), "No Default Shift")
                        new_shift_name = st.selectbox(
                            "Default Shift",
                            options=list(shift_options.keys()),
                            index=list(shift_options.keys()).index(current_shift_name) if current_shift_name in shift_options else 0,
                            key=f"shift_{member['id']}"
                        )
                        new_shift_id = shift_options[new_shift_name]
                    
                    def save_member():
                        try:
                            db.update_team_member(member['id'], new_name, new_role_id, new_active, new_team_id, new_shift_id)
                            st.success("Updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    def delete_member():
                        db.delete_team_member(member['id'])
                        st.rerun()
                    
                    render_save_delete_buttons(member['id'], save_member, delete_member)
        else:
            st.info("No team members found.")


def show_roles_page():
    """Roles management page."""
    st.markdown('<div class="main-header">🎭 Roles</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Role", "📋 View/Edit Roles"])
    
    with tab1:
        st.subheader("Add New Role")
        
        teams = db.get_all_teams()
        
        col1, col2 = st.columns(2)
        
        with col1:
            role_name = st.text_input("Role Name")
            
            team_options = get_options_dict(teams, include_none=True, none_label="No Team")
            selected_team_name = st.selectbox("Team", options=list(team_options.keys()))
            selected_team_id = team_options[selected_team_name]
        
        with col2:
            role_color = st.color_picker("Color", value="#1f77b4")
        
        if st.button("Add Role", type="primary"):
            if role_name:
                try:
                    db.add_role(role_name, role_color, selected_team_id)
                    st.success(f"✅ Added role: {role_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please enter a role name.")
        card_end()
    
    with tab2:
        st.subheader("All Roles")
        
        roles = db.get_all_roles()
        
        if roles:
            for role in roles:
                team_badge = f" [{role.get('team_name', 'No Team')}]" if role.get('team_name') else ""
                with st.expander(f"**{role['name']}**{team_badge}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Role Name", value=role['name'], key=f"role_name_{role['id']}")
                        
                        teams = db.get_all_teams()
                        team_options = get_options_dict(teams, include_none=True, none_label="No Team")
                        
                        current_team = role.get('team_name', 'No Team')
                        new_team_name = st.selectbox(
                            "Team",
                            options=list(team_options.keys()),
                            index=list(team_options.keys()).index(current_team) if current_team in team_options else 0,
                            key=f"role_team_{role['id']}"
                        )
                        new_team_id = team_options[new_team_name]
                    
                    with col2:
                        new_color = st.color_picker("Color", value=role['color'], key=f"role_color_{role['id']}")
                    
                    def save_role():
                        try:
                            db.update_role(role['id'], new_name, new_color, new_team_id)
                            st.success("Updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    def delete_role():
                        try:
                            db.delete_role(role['id'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Cannot delete: {str(e)}")
                            
                    render_save_delete_buttons(role['id'], save_role, delete_role)
        else:
            st.info("No roles found.")


def show_responsibilities_page():
    """Responsibilities management page."""
    st.markdown('<div class="main-header">📋 Responsibilities</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Responsibility", "📋 View/Edit Responsibilities"])
    
    with tab1:
        card_begin("Add New Responsibility")
        
        col1, col2 = st.columns(2)
        
        with col1:
            resp_name = st.text_input("Responsibility Name")
            resp_desc = st.text_area("Description (Optional)")
        with col2:
            resp_color = st.color_picker("Color", value="#ff7f0e")
        
        if st.button("Add Responsibility", type="primary"):
            if resp_name:
                try:
                    db.add_responsibility(resp_name, resp_color, resp_desc)
                    st.success(f"✅ Added responsibility: {resp_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please enter a responsibility name.")
        card_end()
    
    with tab2:
        card_begin("All Responsibilities")
        
        responsibilities = db.get_all_responsibilities()
        
        if responsibilities:
            for resp in responsibilities:
                with st.expander(f"**{resp['name']}**", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Responsibility Name", value=resp['name'], key=f"resp_name_{resp['id']}")
                        new_desc = st.text_area("Description", value=resp.get('description', ''), key=f"resp_desc_{resp['id']}")
                    
                    with col2:
                        new_color = st.color_picker("Color", value=resp['color'], key=f"resp_color_{resp['id']}")
                    
                    def save_resp():
                        try:
                            db.update_responsibility(resp['id'], new_name, new_color, new_desc)
                            st.success("Updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    
                    def delete_resp():
                        try:
                            db.delete_responsibility(resp['id'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Cannot delete: {str(e)}")
                            
                    render_save_delete_buttons(resp['id'], save_resp, delete_resp)
            card_end()
        else:
            st.info("No responsibilities found.")


def show_absences_page():
    """Absences/holidays management page."""
    st.markdown('<div class="main-header">🏖️ Absences & Holidays</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Absence", "📋 View/Edit Absences"])
    
    with tab1:
        card_begin("Add Absence")
        
        members = db.get_all_team_members()
        
        if not members:
            st.warning("⚠️ No team members found. Please add team members first.")
            card_end()
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            member_options = {m['name']: m['id'] for m in members}
            selected_member_name = st.selectbox("Team Member", options=list(member_options.keys()))
            selected_member_id = member_options[selected_member_name]
            
            absence_reason = st.selectbox("Reason", options=["Holiday", "Sick", "Training", "Other"])
        
        with col2:
            start_date = st.date_input("Start Date", value=date.today(), key="absence_start")
            end_date = st.date_input("End Date", value=date.today(), key="absence_end")
        
        if st.button("Add Absence", type="primary"):
            if start_date <= end_date:
                db.add_absence(
                    selected_member_id,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    absence_reason
                )
                st.success("✅ Absence added successfully!")
                st.rerun()
            else:
                st.error("End date must be after start date.")
        card_end()
    
    with tab2:
        st.subheader("All Absences")
        
        absences = db.get_all_absences()
        
        if absences:
            for absence in absences:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 0.8])
                
                with col1:
                    st.text(absence['member_name'])
                with col2:
                    st.text(absence['start_date'])
                with col3:
                    st.text(absence['end_date'])
                with col4:
                    st.text(absence['reason'])
                with col5:
                    if st.button("🗑️", key=f"del_absence_{absence['id']}"):
                        db.delete_absence(absence['id'])
                        st.rerun()
        else:
            st.info("No absences found.")


if __name__ == "__main__":
    main()
