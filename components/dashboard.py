"""
Dashboard Component - User overview and statistics display
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.supabase_client import supabase_client
from utils.logger import setup_logger

logger = setup_logger("dashboard")

class Dashboard:
    def __init__(self):
        self.client = supabase_client.client
    
    def render(self):
        """Render the dashboard page"""
        st.header("📊 Your Progress Dashboard")
        
        user_id = st.session_state.user_id
        
        # Get user data
        goals_data = self._get_user_goals(user_id)
        tasks_data = self._get_user_tasks(user_id)
        
        # Overview metrics
        self._render_overview_metrics(goals_data, tasks_data)
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_goal_progress_chart(goals_data)
            self._render_task_completion_trend(tasks_data)
        
        with col2:
            self._render_category_distribution(goals_data)
            self._render_upcoming_tasks(tasks_data)
        
        # Recent activity
        st.markdown("---")
        self._render_recent_activity(tasks_data)
    
    def _get_user_goals(self, user_id: str):
        """Get user's goals"""
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user goals: {e}")
            return []
    
    def _get_user_tasks(self, user_id: str, days_back: int = 30):
        """Get user's recent tasks"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("scheduled_date", start_date)\
                .order("scheduled_date", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user tasks: {e}")
            return []
    
    def _render_overview_metrics(self, goals_data, tasks_data):
        """Render overview metrics cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        # Goals metrics
        total_goals = len(goals_data)
        active_goals = len([g for g in goals_data if g["status"] == "active"])
        completed_goals = len([g for g in goals_data if g["status"] == "completed"])
        
        # Tasks metrics
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t["status"] == "completed"])
        pending_tasks = len([t for t in tasks_data if t["status"] == "pending"])
        overdue_tasks = len([t for t in tasks_data 
                           if t["status"] in ["pending", "in_progress"] 
                           and datetime.strptime(t["scheduled_date"], "%Y-%m-%d") < datetime.now()])
        
        with col1:
            st.metric("Total Goals", total_goals, f"{active_goals} active")
        
        with col2:
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("Task Completion", f"{completion_rate:.1f}%", f"{completed_tasks}/{total_tasks}")
        
        with col3:
            st.metric("Pending Tasks", pending_tasks, f"{overdue_tasks} overdue" if overdue_tasks > 0 else "On track")
        
        with col4:
            avg_progress = sum(g["progress_percentage"] for g in goals_data) / len(goals_data) if goals_data else 0
            st.metric("Avg Progress", f"{avg_progress:.1f}%", f"{completed_goals} completed")
    
    def _render_goal_progress_chart(self, goals_data):
        """Render goal progress chart"""
        st.subheader("🎯 Goal Progress")
        
        if not goals_data:
            st.info("No goals yet. Create your first goal to see progress!")
            return
        
        # Create progress chart
        df = pd.DataFrame(goals_data)
        
        fig = go.Figure()
        
        for i, goal in enumerate(goals_data[:5]):  # Show top 5 goals
            fig.add_trace(go.Bar(
                x=[goal["progress_percentage"]],
                y=[goal["title"][:30] + "..." if len(goal["title"]) > 30 else goal["title"]],
                orientation='h',
                name=goal["title"],
                marker_color=px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)]
            ))
        
        fig.update_layout(
            title="Goal Progress (%)",
            xaxis_title="Progress %",
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_category_distribution(self, goals_data):
        """Render goal category distribution"""
        st.subheader("📂 Goals by Category")
        
        if not goals_data:
            st.info("No goals to categorize yet.")
            return
        
        # Count goals by category
        categories = {}
        for goal in goals_data:
            category = goal.get("category", "Other")
            categories[category] = categories.get(category, 0) + 1
        
        if categories:
            fig = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title="Distribution by Category"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_task_completion_trend(self, tasks_data):
        """Render task completion trend over time"""
        st.subheader("📈 Task Completion Trend")
        
        if not tasks_data:
            st.info("No task data available yet.")
            return
        
        # Group tasks by date and status
        df = pd.DataFrame(tasks_data)
        df["scheduled_date"] = pd.to_datetime(df["scheduled_date"])
        
        # Get last 14 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=13)
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        completion_data = []
        
        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            day_tasks = [t for t in tasks_data if t["scheduled_date"] == date_str]
            completed = len([t for t in day_tasks if t["status"] == "completed"])
            total = len(day_tasks)
            
            completion_data.append({
                "date": date.strftime("%m-%d"),
                "completion_rate": (completed / total * 100) if total > 0 else 0,
                "completed": completed,
                "total": total
            })
        
        if completion_data:
            trend_df = pd.DataFrame(completion_data)
            fig = px.line(
                trend_df,
                x="date",
                y="completion_rate",
                title="Daily Completion Rate (%)",
                markers=True
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_upcoming_tasks(self, tasks_data):
        """Render upcoming tasks"""
        st.subheader("⏰ Upcoming Tasks")
        
        # Get today's and tomorrow's tasks
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        today_tasks = [t for t in tasks_data if t["scheduled_date"] == today and t["status"] == "pending"]
        tomorrow_tasks = [t for t in tasks_data if t["scheduled_date"] == tomorrow and t["status"] == "pending"]
        
        if today_tasks:
            st.write("**Today:**")
            for task in today_tasks[:3]:  # Show max 3
                priority_emoji = "🔴" if task["priority"] >= 4 else "🟡" if task["priority"] >= 3 else "🟢"
                duration = f" ({task['estimated_duration_minutes']}min)" if task.get("estimated_duration_minutes") else ""
                st.write(f"{priority_emoji} {task['title']}{duration}")
        
        if tomorrow_tasks:
            st.write("**Tomorrow:**")
            for task in tomorrow_tasks[:3]:  # Show max 3
                priority_emoji = "🔴" if task["priority"] >= 4 else "🟡" if task["priority"] >= 3 else "🟢"
                duration = f" ({task['estimated_duration_minutes']}min)" if task.get("estimated_duration_minutes") else ""
                st.write(f"{priority_emoji} {task['title']}{duration}")
        
        if not today_tasks and not tomorrow_tasks:
            st.info("No upcoming tasks. Great job staying on top of things!")
    
    def _render_recent_activity(self, tasks_data):
        """Render recent activity feed"""
        st.subheader("🔔 Recent Activity")
        
        # Get recently completed tasks
        recent_completed = [
            t for t in tasks_data 
            if t["status"] == "completed" and t.get("completed_at")
        ]
        
        # Sort by completion time (most recent first)
        recent_completed.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
        
        if recent_completed:
            for task in recent_completed[:5]:  # Show last 5 completed tasks
                completed_date = datetime.fromisoformat(task["completed_at"].replace('Z', '+00:00'))
                time_ago = self._get_time_ago(completed_date)
                
                st.write(f"✅ **{task['title']}** - {time_ago}")
                if task.get("completion_notes"):
                    st.write(f"   📝 {task['completion_notes']}")
        else:
            st.info("No recent activity to show.")
    
    def _get_time_ago(self, datetime_obj):
        """Get human-readable time ago string"""
        now = datetime.now(datetime_obj.tzinfo)
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"