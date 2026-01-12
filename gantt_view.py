import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd


def create_daily_gantt(schedules: List[Dict], absences: List[Dict], selected_date: str) -> go.Figure:
    """
    Create a daily Gantt chart showing shift schedules.
    
    Args:
        schedules: List of schedule dictionaries with member, shift, and responsibility info
        absences: List of absences for the selected date
        selected_date: Date string in YYYY-MM-DD format
    
    Returns:
        Plotly figure object
    """
    
    if not schedules and not absences:
        # Return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title=f"No schedules or absences for {selected_date}",
            height=300
        )
        return fig
    
    # Parse the date
    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        date_obj = datetime.now()
    
    # Prepare data for Gantt chart
    gantt_data = []
    
    # Add schedules
    for schedule in schedules:
        start_time = schedule['start_time']  # e.g., "07:00"
        end_time = schedule['end_time']      # e.g., "15:00"
        
        # Create datetime objects for the shift
        start_dt = datetime.strptime(f"{selected_date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{selected_date} {end_time}", "%Y-%m-%d %H:%M")
        
        # Get color from responsibility, or use default
        color = schedule.get('responsibility_color', '#808080')
        
        gantt_data.append({
            'Member': schedule['member_name'],
            'Start': start_dt,
            'Finish': end_dt,
            'Shift': schedule['shift_name'],
            'Responsibility': schedule.get('responsibility_name', 'Unassigned'),
            'Role': schedule.get('role_name', 'No Role'),
            'Color': color,
            'Type': 'Schedule'
        })
    
    # Add absences
    absence_members = set()
    for absence in absences:
        member_name = absence['member_name']
        absence_members.add(member_name)
        
        # Show absence as full day (7am to 10pm to cover all shifts)
        start_dt = datetime.strptime(f"{selected_date} 07:00", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{selected_date} 22:00", "%Y-%m-%d %H:%M")
        
        gantt_data.append({
            'Member': member_name,
            'Start': start_dt,
            'Finish': end_dt,
            'Shift': 'ABSENT',
            'Responsibility': absence['reason'],
            'Role': '',  # No role for absences
            'Color': '#FF6B6B',  # Red for absences
            'Type': 'Absence'
        })
    
    if not gantt_data:
        fig = go.Figure()
        fig.update_layout(
            title=f"No data for {selected_date}",
            height=300
        )
        return fig
    
    # Create the figure
    fig = go.Figure()
    
    # Sort by member name for consistent display
    gantt_data.sort(key=lambda x: x['Member'])
    
    # Get unique members for Y-axis
    unique_members = []
    seen = set()
    for item in gantt_data:
        if item['Member'] not in seen:
            unique_members.append(item['Member'])
            seen.add(item['Member'])
    
    # Add bars for each schedule/absence
    for item in gantt_data:
        # Calculate duration in hours for display
        duration = (item['Finish'] - item['Start']).total_seconds() / 3600
        
        hover_text = (
            f"<b>{item['Member']}</b><br>"
            f"Shift: {item['Shift']}<br>"
            f"Time: {item['Start'].strftime('%H:%M')} - {item['Finish'].strftime('%H:%M')}<br>"
            f"Responsibility: {item['Responsibility']}<br>"
            f"Duration: {duration:.1f} hours"
        )
        
        # Determine pattern for absences
        pattern_shape = ""
        if item['Type'] == 'Absence':
            pattern_shape = "/"
        
        # Prepare text label (role name)
        text_label = item.get('Responsibility', '')
        
        fig.add_trace(go.Bar(
            name=item['Responsibility'],
            y=[item['Member']],
            x=[duration],
            base=[(item['Start'] - datetime.strptime(f"{selected_date} 00:00", "%Y-%m-%d %H:%M")).total_seconds() / 3600],
            orientation='h',
            marker=dict(
                color=item['Color'],
                line=dict(color='rgba(255,255,255,0.1)', width=0.5),
                pattern_shape=pattern_shape
            ),
            text=text_label,
            textposition='inside',
            textfont=dict(
                size=11,
                color='white',
                family='Outfit, sans-serif'
            ),
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Shift Schedule - {date_obj.strftime('%A, %B %d, %Y')}",
            font=dict(size=18, family="Outfit, sans-serif", color="#f0f0f0"),
            x=0.08
        ),
        xaxis=dict(
            title=dict(
                text="Time of Day",
                font=dict(size=12, family="Outfit, sans-serif", color="#d0d0d0")
            ),
            tickfont=dict(size=10, family="Outfit, sans-serif", color="#c0c0c0"),
            tickmode='linear',
            tick0=7,
            dtick=1,
            range=[7, 22],
            ticktext=[f"{h:02d}:00" for h in range(7, 23)],
            tickvals=list(range(7, 23)),
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=12, family="Outfit, sans-serif", color="#f0f0f0"),
            categoryorder='array',
            categoryarray=unique_members[::-1]
        ),
        barmode='overlay',
        height=max(400, len(unique_members) * 60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor="#2a2a2a",
            font=dict(
                size=12,
                family="Outfit, sans-serif",
                color="#f0f0f0"
            ),
            bordercolor="rgba(255,255,255,0.3)"
        ),
        margin=dict(l=150, r=50, t=100, b=100)
    )
    
    # Add vertical lines for shift boundaries (7am, 2pm, 3pm, 5pm, 10pm)
    shift_times = [7, 14, 15, 17, 22]
    for time in shift_times:
        fig.add_vline(
            x=time,
            line_dash="dash",
            line_color="gray",
            opacity=0.3,
            annotation_text=f"{time:02d}:00" if time in [7, 14, 22] else "",
            annotation_position="top"
        )
    
    return fig


def create_weekly_overview(schedules: List[Dict], start_date: str) -> pd.DataFrame:
    """
    Create a weekly overview DataFrame for display.
    
    Args:
        schedules: List of schedule dictionaries
        start_date: Start date of the week in YYYY-MM-DD format
    
    Returns:
        DataFrame with weekly schedule summary
    """
    if not schedules:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(schedules)
    
    # Group by date and member to create summary
    summary = df.groupby(['date', 'member_name']).agg({
        'shift_name': lambda x: ', '.join(sorted(set(x))),
        'responsibility_name': lambda x: ', '.join([r for r in x if r])
    }).reset_index()
    
    summary.columns = ['Date', 'Member', 'Shifts', 'Responsibilities']
    
    return summary
