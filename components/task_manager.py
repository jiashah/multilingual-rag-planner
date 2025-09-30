"""
Task Manager Component - Manage daily tasks and track progress
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.supabase_client import supabase_client
from utils.logger import setup_logger

logger = setup_logger("task_manager")

class TaskManager:
    def __init__(self):
        self.client = supabase_client.client
    
    def render(self):
        """Render the task manager page"""
        st.header("📝 Task Manager")
        
        user_id = st.session_state.user_id
        
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Today's Tasks", "Upcoming Tasks", "All Tasks", "Create Task"])
        
        with tab1:
            self._render_todays_tasks(user_id)
        
        with tab2:
            self._render_upcoming_tasks(user_id)
        
        with tab3:
            self._render_all_tasks(user_id)
        
        with tab4:
            self._render_create_task_form(user_id)
    
    def _render_todays_tasks(self, user_id: str):
        """Render today's tasks"""
        st.subheader("📅 Today's Tasks")
        
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = self._get_tasks_for_date(user_id, today)
        
        if not tasks:
            st.info("No tasks scheduled for today. Great job staying organized!")
            return
        
        # Progress summary
        completed_tasks = len([t for t in tasks if t["status"] == "completed"])
        total_tasks = len(tasks)
        progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", total_tasks)
        with col2:
            st.metric("Completed", completed_tasks)
        with col3:
            st.metric("Progress", f"{progress:.1f}%")
        
        st.progress(progress / 100)
        
        # Task list
        st.markdown("---")
        
        # Group tasks by status
        pending_tasks = [t for t in tasks if t["status"] == "pending"]
        in_progress_tasks = [t for t in tasks if t["status"] == "in_progress"]
        completed_tasks_list = [t for t in tasks if t["status"] == "completed"]
        
        # Pending tasks
        if pending_tasks:
            st.subheader("⏳ Pending Tasks")
            for task in pending_tasks:
                self._render_task_card(task, user_id, show_actions=True)
        
        # In progress tasks
        if in_progress_tasks:
            st.subheader("🔄 In Progress")
            for task in in_progress_tasks:
                self._render_task_card(task, user_id, show_actions=True)
        
        # Completed tasks
        if completed_tasks_list:
            with st.expander(f"✅ Completed Tasks ({len(completed_tasks_list)})"):
                for task in completed_tasks_list:
                    self._render_task_card(task, user_id, show_actions=False)
    
    def _render_upcoming_tasks(self, user_id: str):
        """Render upcoming tasks (next 7 days)"""
        st.subheader("📆 Upcoming Tasks (Next 7 Days)")
        
        # Date range
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        tasks = self._get_tasks_for_date_range(user_id, start_date, end_date)
        
        if not tasks:
            st.info("No upcoming tasks scheduled. Consider planning ahead!")
            return
        
        # Group tasks by date
        tasks_by_date = {}
        for task in tasks:
            date = task["scheduled_date"]
            if date not in tasks_by_date:
                tasks_by_date[date] = []
            tasks_by_date[date].append(task)
        
        # Display tasks by date
        for date in sorted(tasks_by_date.keys()):
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            formatted_date = date_obj.strftime("%B %d, %Y")
            
            st.subheader(f"{day_name}, {formatted_date}")
            
            day_tasks = tasks_by_date[date]
            for task in day_tasks:
                self._render_task_card(task, user_id, show_actions=True)
            
            st.markdown("---")
    
    def _render_all_tasks(self, user_id: str):
        """Render all tasks with filtering and search"""
        st.subheader("📋 All Tasks")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox("Status", ["all", "pending", "in_progress", "completed", "skipped"])
        
        with col2:
            # Get user's goals for filtering
            goals = self._get_user_goals(user_id)
            goal_options = ["all"] + [g["title"] for g in goals]
            goal_filter = st.selectbox("Goal", goal_options)
        
        with col3:
            date_range = st.selectbox("Date Range", ["all", "today", "this_week", "this_month", "overdue"])
        
        with col4:
            priority_filter = st.selectbox("Priority", ["all", "1", "2", "3", "4", "5"])
        
        # Search box
        search_query = st.text_input("🔍 Search tasks", placeholder="Search by title or description...")
        
        # Get tasks
        tasks = self._get_user_tasks(user_id)
        
        # Apply filters
        filtered_tasks = self._apply_filters(tasks, {
            "status": status_filter,
            "goal": goal_filter,
            "date_range": date_range,
            "priority": priority_filter,
            "search": search_query
        }, goals)
        
        if not filtered_tasks:
            st.info("No tasks match your filters.")
            return
        
        # Show results count
        st.write(f"Found {len(filtered_tasks)} task(s)")
        
        # Display tasks
        for task in filtered_tasks:
            self._render_task_card(task, user_id, show_actions=True)
            st.markdown("---")
    
    def _render_create_task_form(self, user_id: str):
        """Render create task form"""
        st.subheader("➕ Create New Task")
        
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Task Title *", placeholder="What needs to be done?")
                description = st.text_area("Description", placeholder="Detailed description of the task...")
                scheduled_date = st.date_input("Scheduled Date", value=datetime.now().date())
                priority = st.slider("Priority", 1, 5, 3, help="1=Low, 5=High")
            
            with col2:
                # Get user's goals for assignment
                goals = self._get_user_goals(user_id)
                goal_options = ["None"] + [g["title"] for g in goals]
                goal_assignment = st.selectbox("Assign to Goal", goal_options)
                
                estimated_duration = st.number_input("Estimated Duration (minutes)", min_value=5, max_value=480, value=30)
                category = st.selectbox("Category", ["work", "study", "practice", "research", "review", "break", "other"])
                
            submitted = st.form_submit_button("Create Task", type="primary")
            
            if submitted:
                if not title:
                    st.error("Please enter a task title")
                else:
                    # Find goal ID if assigned
                    goal_id = None
                    if goal_assignment != "None":
                        selected_goal = next((g for g in goals if g["title"] == goal_assignment), None)
                        if selected_goal:
                            goal_id = selected_goal["id"]
                    
                    task_data = {
                        "user_id": user_id,
                        "goal_id": goal_id,
                        "title": title,
                        "description": description,
                        "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                        "priority": priority,
                        "estimated_duration_minutes": estimated_duration,
                        "status": "pending",
                        "ai_generated": False
                    }
                    
                    self._create_task(task_data)
    
    def _render_task_card(self, task: dict, user_id: str, show_actions: bool = True):
        """Render a single task card"""
        # Priority indicator
        priority_colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🔥"}
        priority_indicator = priority_colors.get(task.get("priority", 3), "⚪")
        
        # Status indicator
        status_indicators = {
            "pending": "⏳",
            "in_progress": "🔄", 
            "completed": "✅",
            "skipped": "⏭️"
        }
        status_indicator = status_indicators.get(task["status"], "❓")
        
        # Create container
        container = st.container()
        
        with container:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Task title with status and priority
                st.write(f"{status_indicator} {priority_indicator} **{task['title']}**")
                
                # Description
                if task.get("description"):
                    st.write(task["description"])
                
                # Task details
                details = []
                if task.get("estimated_duration_minutes"):
                    details.append(f"⏱️ {task['estimated_duration_minutes']} min")
                
                if task.get("scheduled_date"):
                    scheduled_date = datetime.strptime(task["scheduled_date"], "%Y-%m-%d")
                    if scheduled_date.date() == datetime.now().date():
                        details.append("📅 Today")
                    elif scheduled_date.date() == (datetime.now() + timedelta(days=1)).date():
                        details.append("📅 Tomorrow")
                    else:
                        details.append(f"📅 {task['scheduled_date']}")
                
                if task.get("goal_id"):
                    # Get goal name
                    goal = self._get_goal_by_id(task["goal_id"])
                    if goal:
                        details.append(f"🎯 {goal['title']}")
                
                if details:
                    st.write(" | ".join(details))
            
            with col2:
                if show_actions:
                    self._render_task_actions(task, user_id)
    
    def _render_task_actions(self, task: dict, user_id: str):
        """Render task action buttons"""
        task_id = task["id"]
        
        if task["status"] == "pending":
            if st.button("▶️", key=f"start_{task_id}", help="Start task"):
                self._update_task_status(task_id, "in_progress")
                st.rerun()
            
            if st.button("✅", key=f"complete_{task_id}", help="Mark complete"):
                self._complete_task(task, user_id)
                st.rerun()
                
        elif task["status"] == "in_progress":
            if st.button("✅", key=f"complete_{task_id}", help="Mark complete"):
                self._complete_task(task, user_id)
                st.rerun()
            
            if st.button("⏸️", key=f"pause_{task_id}", help="Pause task"):
                self._update_task_status(task_id, "pending")
                st.rerun()
        
        elif task["status"] == "completed":
            if st.button("↩️", key=f"reopen_{task_id}", help="Reopen task"):
                self._update_task_status(task_id, "pending")
                st.rerun()
        
        # Skip/Delete options
        with st.popover("⋯"):
            if task["status"] in ["pending", "in_progress"]:
                if st.button("⏭️ Skip", key=f"skip_{task_id}"):
                    self._update_task_status(task_id, "skipped")
                    st.rerun()
            
            if st.button("🗑️ Delete", key=f"delete_{task_id}"):
                self._delete_task(task_id)
                st.rerun()
    
    def _complete_task(self, task: dict, user_id: str):
        """Complete a task with optional notes"""
        with st.form(f"complete_task_{task['id']}"):
            st.write(f"Completing: **{task['title']}**")
            completion_notes = st.text_area("Completion Notes (Optional)", 
                                          placeholder="Any notes about completing this task...")
            
            submitted = st.form_submit_button("Complete Task")
            
            if submitted:
                update_data = {
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "completion_notes": completion_notes
                }
                
                try:
                    self.client.table("daily_tasks")\
                        .update(update_data)\
                        .eq("id", task["id"])\
                        .execute()
                    
                    st.success("Task completed! 🎉")
                    
                    # Update goal progress if applicable
                    if task.get("goal_id"):
                        self._update_goal_progress(task["goal_id"])
                        
                except Exception as e:
                    logger.error(f"Failed to complete task: {e}")
                    st.error("Failed to complete task.")
    
    def _get_tasks_for_date(self, user_id: str, date: str):
        """Get tasks for a specific date"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("scheduled_date", date)\
                .order("priority", desc=True)\
                .order("created_at")\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get tasks for date: {e}")
            return []
    
    def _get_tasks_for_date_range(self, user_id: str, start_date: str, end_date: str):
        """Get tasks for a date range"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("scheduled_date", start_date)\
                .lte("scheduled_date", end_date)\
                .order("scheduled_date")\
                .order("priority", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get tasks for date range: {e}")
            return []
    
    def _get_user_tasks(self, user_id: str, limit: int = 100):
        """Get user's tasks"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("scheduled_date", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user tasks: {e}")
            return []
    
    def _get_user_goals(self, user_id: str):
        """Get user's goals"""
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user goals: {e}")
            return []
    
    def _get_goal_by_id(self, goal_id: str):
        """Get goal by ID"""
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("id", goal_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get goal by ID: {e}")
            return None
    
    def _apply_filters(self, tasks: list, filters: dict, goals: list):
        """Apply filters to tasks list"""
        filtered = tasks
        
        # Status filter
        if filters["status"] != "all":
            filtered = [t for t in filtered if t["status"] == filters["status"]]
        
        # Goal filter
        if filters["goal"] != "all":
            goal = next((g for g in goals if g["title"] == filters["goal"]), None)
            if goal:
                filtered = [t for t in filtered if t.get("goal_id") == goal["id"]]
        
        # Date range filter
        today = datetime.now().date()
        if filters["date_range"] == "today":
            today_str = today.strftime("%Y-%m-%d")
            filtered = [t for t in filtered if t["scheduled_date"] == today_str]
        elif filters["date_range"] == "this_week":
            week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            week_end = (today + timedelta(days=6-today.weekday())).strftime("%Y-%m-%d")
            filtered = [t for t in filtered if week_start <= t["scheduled_date"] <= week_end]
        elif filters["date_range"] == "this_month":
            month_start = today.replace(day=1).strftime("%Y-%m-%d")
            filtered = [t for t in filtered if t["scheduled_date"] >= month_start]
        elif filters["date_range"] == "overdue":
            today_str = today.strftime("%Y-%m-%d")
            filtered = [t for t in filtered 
                       if t["scheduled_date"] < today_str and t["status"] in ["pending", "in_progress"]]
        
        # Priority filter
        if filters["priority"] != "all":
            priority = int(filters["priority"])
            filtered = [t for t in filtered if t.get("priority") == priority]
        
        # Search filter
        if filters["search"]:
            query = filters["search"].lower()
            filtered = [t for t in filtered 
                       if query in t["title"].lower() or 
                       (t.get("description") and query in t["description"].lower())]
        
        return filtered
    
    def _create_task(self, task_data: dict):
        """Create a new task"""
        try:
            response = self.client.table("daily_tasks").insert(task_data).execute()
            
            if response.data:
                st.success("✅ Task created successfully!")
            else:
                st.error("Failed to create task.")
                
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            st.error("Failed to create task.")
    
    def _update_task_status(self, task_id: str, new_status: str):
        """Update task status"""
        try:
            update_data = {"status": new_status}
            
            if new_status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()
            
            self.client.table("daily_tasks")\
                .update(update_data)\
                .eq("id", task_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            st.error("Failed to update task status.")
    
    def _delete_task(self, task_id: str):
        """Delete a task"""
        try:
            self.client.table("daily_tasks")\
                .delete()\
                .eq("id", task_id)\
                .execute()
            
            st.success("Task deleted.")
            
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            st.error("Failed to delete task.")
    
    def _update_goal_progress(self, goal_id: str):
        """Update goal progress based on completed tasks"""
        try:
            # Get all tasks for the goal
            response = self.client.table("daily_tasks")\
                .select("status")\
                .eq("goal_id", goal_id)\
                .execute()
            
            tasks = response.data if response.data else []
            
            if not tasks:
                return
            
            completed_tasks = len([t for t in tasks if t["status"] == "completed"])
            total_tasks = len(tasks)
            progress_percentage = int((completed_tasks / total_tasks) * 100)
            
            # Update goal progress
            self.client.table("goals")\
                .update({"progress_percentage": progress_percentage})\
                .eq("id", goal_id)\
                .execute()
            
        except Exception as e:
            logger.error(f"Failed to update goal progress: {e}")