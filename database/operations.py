"""
Database Operations - CRUD operations for user data persistence
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database.supabase_client import supabase_client
from utils.logger import setup_logger

logger = setup_logger("database_operations")

class DatabaseOperations:
    def __init__(self):
        self.client = supabase_client.client
    
    # User Profile Operations
    def create_user_profile(self, user_data: Dict[str, Any]) -> bool:
        """Create or update user profile"""
        try:
            response = self.client.table("user_profiles")\
                .upsert(user_data)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            response = self.client.table("user_profiles")\
                .select("*")\
                .eq("id", user_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            response = self.client.table("user_profiles")\
                .update(updates)\
                .eq("id", user_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    # Goal Operations
    def create_goal(self, goal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new goal"""
        try:
            response = self.client.table("goals")\
                .insert(goal_data)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            return None
    
    def get_user_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's goals with optional status filter"""
        try:
            query = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user goals: {e}")
            return []
    
    def get_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
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
    
    def update_goal(self, goal_id: str, updates: Dict[str, Any]) -> bool:
        """Update goal"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            response = self.client.table("goals")\
                .update(updates)\
                .eq("id", goal_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to update goal: {e}")
            return False
    
    def delete_goal(self, goal_id: str) -> bool:
        """Delete goal (and associated tasks)"""
        try:
            # First delete associated tasks
            self.client.table("daily_tasks")\
                .delete()\
                .eq("goal_id", goal_id)\
                .execute()
            
            # Then delete the goal
            response = self.client.table("goals")\
                .delete()\
                .eq("id", goal_id)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete goal: {e}")
            return False
    
    def get_goal_progress(self, goal_id: str) -> Dict[str, Any]:
        """Get goal progress statistics"""
        try:
            # Get goal info
            goal = self.get_goal_by_id(goal_id)
            if not goal:
                return {"error": "Goal not found"}
            
            # Get task statistics
            response = self.client.table("daily_tasks")\
                .select("status")\
                .eq("goal_id", goal_id)\
                .execute()
            
            tasks = response.data if response.data else []
            total_tasks = len(tasks)
            
            if total_tasks == 0:
                return {
                    "goal": goal,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "pending_tasks": 0,
                    "completion_rate": 0
                }
            
            completed_tasks = len([t for t in tasks if t["status"] == "completed"])
            pending_tasks = len([t for t in tasks if t["status"] in ["pending", "in_progress"]])
            completion_rate = (completed_tasks / total_tasks) * 100
            
            return {
                "goal": goal,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "completion_rate": completion_rate
            }
        except Exception as e:
            logger.error(f"Failed to get goal progress: {e}")
            return {"error": str(e)}
    
    # Task Operations
    def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new task"""
        try:
            response = self.client.table("daily_tasks")\
                .insert(task_data)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    def create_multiple_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple tasks"""
        try:
            response = self.client.table("daily_tasks")\
                .insert(tasks_data)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to create multiple tasks: {e}")
            return []
    
    def get_user_tasks(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's tasks"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("scheduled_date", desc=True)\
                .order("priority", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user tasks: {e}")
            return []
    
    def get_tasks_by_date(self, user_id: str, date: str) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to get tasks by date: {e}")
            return []
    
    def get_tasks_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to get tasks by date range: {e}")
            return []
    
    def get_goal_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific goal"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("goal_id", goal_id)\
                .order("scheduled_date")\
                .order("priority", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get goal tasks: {e}")
            return []
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            response = self.client.table("daily_tasks")\
                .update(updates)\
                .eq("id", task_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def complete_task(self, task_id: str, completion_notes: str = None) -> bool:
        """Mark task as completed"""
        try:
            updates = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if completion_notes:
                updates["completion_notes"] = completion_notes
            
            response = self.client.table("daily_tasks")\
                .update(updates)\
                .eq("id", task_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        try:
            response = self.client.table("daily_tasks")\
                .delete()\
                .eq("id", task_id)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False
    
    def get_overdue_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .lt("scheduled_date", today)\
                .in_("status", ["pending", "in_progress"])\
                .order("scheduled_date")\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {e}")
            return []
    
    # Knowledge Document Operations
    def create_knowledge_document(self, doc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a knowledge document entry"""
        try:
            response = self.client.table("knowledge_documents")\
                .insert(doc_data)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create knowledge document: {e}")
            return None
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's knowledge documents"""
        try:
            response = self.client.table("knowledge_documents")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            return []
    
    def update_document_embedding_status(self, doc_id: str, status: str) -> bool:
        """Update document embedding status"""
        try:
            response = self.client.table("knowledge_documents")\
                .update({"embedding_status": status})\
                .eq("id", doc_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to update document embedding status: {e}")
            return False
    
    def delete_knowledge_document(self, doc_id: str, user_id: str) -> bool:
        """Delete knowledge document"""
        try:
            response = self.client.table("knowledge_documents")\
                .delete()\
                .eq("id", doc_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge document: {e}")
            return False
    
    # Analytics and Reporting
    def get_user_analytics(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get user analytics data"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # Get tasks in date range
            tasks = self.get_tasks_by_date_range(user_id, start_date, datetime.now().strftime("%Y-%m-%d"))
            goals = self.get_user_goals(user_id)
            
            # Calculate metrics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t["status"] == "completed"])
            
            # Tasks by status
            status_counts = {}
            for task in tasks:
                status = task["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Tasks by priority
            priority_counts = {}
            for task in tasks:
                priority = task.get("priority", 3)
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Goal statistics
            active_goals = len([g for g in goals if g["status"] == "active"])
            completed_goals = len([g for g in goals if g["status"] == "completed"])
            
            # Completion rate by day (last 7 days)
            daily_completion = {}
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                day_tasks = [t for t in tasks if t["scheduled_date"] == date]
                completed = len([t for t in day_tasks if t["status"] == "completed"])
                total = len(day_tasks)
                daily_completion[date] = {
                    "total": total,
                    "completed": completed,
                    "rate": (completed / total * 100) if total > 0 else 0
                }
            
            return {
                "period_days": days_back,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "status_distribution": status_counts,
                "priority_distribution": priority_counts,
                "active_goals": active_goals,
                "completed_goals": completed_goals,
                "daily_completion": daily_completion
            }
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {"error": str(e)}
    
    # Session Tracking
    def create_user_session(self, session_data: Dict[str, Any]) -> bool:
        """Create a user session record"""
        try:
            response = self.client.table("user_sessions")\
                .insert(session_data)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return False
    
    def update_user_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update user session"""
        try:
            response = self.client.table("user_sessions")\
                .update(updates)\
                .eq("id", session_id)\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Failed to update user session: {e}")
            return False
    
    # Utility Functions
    def bulk_update_goal_progress(self, user_id: str) -> bool:
        """Update progress for all user goals based on completed tasks"""
        try:
            goals = self.get_user_goals(user_id, status="active")
            
            for goal in goals:
                goal_tasks = self.get_goal_tasks(goal["id"])
                
                if not goal_tasks:
                    continue
                
                completed_tasks = len([t for t in goal_tasks if t["status"] == "completed"])
                total_tasks = len(goal_tasks)
                progress_percentage = int((completed_tasks / total_tasks) * 100)
                
                self.update_goal(goal["id"], {"progress_percentage": progress_percentage})
            
            return True
        except Exception as e:
            logger.error(f"Failed to bulk update goal progress: {e}")
            return False
    
    def cleanup_old_sessions(self, days_old: int = 30) -> bool:
        """Clean up old user sessions"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            response = self.client.table("user_sessions")\
                .delete()\
                .lt("started_at", cutoff_date)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return False

# Global instance
db_ops = DatabaseOperations()