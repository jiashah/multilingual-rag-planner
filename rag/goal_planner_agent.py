"""
Goal Planning Agent - AI-powered system for breaking down goals into daily tasks
Uses LLM and RAG system for intelligent task generation
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from database.supabase_client import supabase_client
from rag.rag_system import RAGSystem
from utils.logger import setup_logger

logger = setup_logger("goal_planner_agent")

class GoalPlannerAgent:
    def __init__(self):
        self.client = supabase_client.client
        self.rag_system = RAGSystem()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for task generation"""
        try:
            if os.getenv("OPENAI_API_KEY"):
                return ChatOpenAI(
                    temperature=0.7,
                    model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            else:
                logger.warning("OpenAI API key not found. Goal planning features will be limited.")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    def analyze_goal(self, goal_description: str, user_id: str) -> Dict[str, Any]:
        """
        Analyze a goal and extract key information
        
        Args:
            goal_description (str): Description of the goal
            user_id (str): User ID
            
        Returns:
            Dict containing goal analysis
        """
        try:
            if not self.llm:
                return {"error": "LLM not available"}
            
            # Get relevant documents from user's knowledge base
            relevant_docs = self.rag_system.search_similar_documents(
                goal_description, user_id, k=3
            )
            
            context = "\n".join([doc["content"] for doc in relevant_docs[:3]])
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are an expert goal analysis assistant. Analyze the given goal and provide structured information to help with planning.
                
                Consider the user's personal context if provided.
                
                Return your analysis in the following JSON format:
                {
                    "category": "career|health|education|personal|finance|relationship|hobby|other",
                    "priority": 1-5 (5 being highest),
                    "estimated_duration_weeks": number,
                    "complexity": "low|medium|high",
                    "required_skills": ["skill1", "skill2"],
                    "potential_obstacles": ["obstacle1", "obstacle2"],
                    "success_metrics": ["metric1", "metric2"],
                    "recommended_approach": "brief description of approach"
                }"""),
                HumanMessage(content=f"""
                User's Context (from their documents):
                {context}
                
                Goal to analyze: {goal_description}
                
                Please analyze this goal and provide structured information in JSON format.
                """)
            ])
            
            response = self.llm(prompt.format_messages())
            
            try:
                analysis = json.loads(response.content)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "category": "personal",
                    "priority": 3,
                    "estimated_duration_weeks": 12,
                    "complexity": "medium",
                    "required_skills": [],
                    "potential_obstacles": [],
                    "success_metrics": [],
                    "recommended_approach": "Break down into smaller, manageable tasks"
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze goal: {e}")
            return {"error": str(e)}
    
    def generate_milestone_plan(self, goal: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """
        Generate milestone plan for a goal
        
        Args:
            goal (Dict): Goal information
            user_id (str): User ID
            
        Returns:
            List of milestones
        """
        try:
            if not self.llm:
                return []
            
            # Get user context
            relevant_docs = self.rag_system.search_similar_documents(
                goal["title"], user_id, k=3
            )
            context = "\n".join([doc["content"] for doc in relevant_docs[:3]])
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a goal planning expert. Create a milestone plan for the given goal.
                
                Return your response as a JSON array of milestones:
                [
                    {
                        "title": "Milestone title",
                        "description": "Detailed description",
                        "target_week": week_number,
                        "success_criteria": "What defines completion",
                        "estimated_hours": hours_needed
                    }
                ]
                
                Create 3-6 meaningful milestones that build towards the main goal."""),
                HumanMessage(content=f"""
                User's Context:
                {context}
                
                Goal: {goal["title"]}
                Description: {goal.get("description", "")}
                Target Date: {goal.get("target_completion_date", "Not specified")}
                Category: {goal.get("category", "Not specified")}
                
                Create a milestone plan for this goal.
                """)
            ])
            
            response = self.llm(prompt.format_messages())
            
            try:
                milestones = json.loads(response.content)
                return milestones if isinstance(milestones, list) else []
            except json.JSONDecodeError:
                logger.error("Failed to parse milestone JSON")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate milestone plan: {e}")
            return []
    
    def generate_daily_tasks(self, goal: Dict[str, Any], user_id: str, 
                           target_date: datetime, num_days: int = 7) -> List[Dict[str, Any]]:
        """
        Generate daily tasks for a specific goal
        
        Args:
            goal (Dict): Goal information
            user_id (str): User ID
            target_date (datetime): Starting date for task generation
            num_days (int): Number of days to generate tasks for
            
        Returns:
            List of daily tasks
        """
        try:
            if not self.llm:
                return []
            
            # Get user's existing tasks to avoid conflicts
            existing_tasks = self._get_existing_tasks(user_id, target_date, num_days)
            
            # Get relevant context from user's documents
            relevant_docs = self.rag_system.search_similar_documents(
                f"{goal['title']} {goal.get('description', '')}", user_id, k=3
            )
            context = "\n".join([doc["content"] for doc in relevant_docs[:3]])
            
            # Get user preferences
            user_profile = self._get_user_profile(user_id)
            daily_limit = user_profile.get("daily_task_limit", 10) if user_profile else 10
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=f"""You are an expert task planning assistant. Generate daily tasks for the given goal.
                
                Guidelines:
                - Generate maximum {daily_limit} tasks per day
                - Tasks should be specific, actionable, and measurable
                - Consider the user's existing commitments
                - Balance work/study tasks with breaks and reflection
                - Estimate realistic time durations (15-120 minutes per task)
                
                Return JSON array of tasks:
                [
                    {{
                        "scheduled_date": "YYYY-MM-DD",
                        "title": "Task title",
                        "description": "Detailed description",
                        "estimated_duration_minutes": number,
                        "priority": 1-5,
                        "category": "work|study|practice|research|review|break"
                    }}
                ]"""),
                HumanMessage(content=f"""
                User's Context:
                {context}
                
                Goal: {goal["title"]}
                Description: {goal.get("description", "")}
                Category: {goal.get("category", "")}
                Priority: {goal.get("priority", 3)}
                
                Generate tasks from {target_date.strftime('%Y-%m-%d')} for {num_days} days.
                
                User's existing tasks to avoid conflicts:
                {json.dumps(existing_tasks, indent=2)}
                
                Create a balanced daily task plan.
                """)
            ])
            
            response = self.llm(prompt.format_messages())
            
            try:
                tasks = json.loads(response.content)
                if isinstance(tasks, list):
                    # Add goal_id and user_id to each task
                    for task in tasks:
                        task["goal_id"] = goal["id"]
                        task["user_id"] = user_id
                        task["ai_generated"] = True
                    return tasks
                return []
            except json.JSONDecodeError:
                logger.error("Failed to parse tasks JSON")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate daily tasks: {e}")
            return []
    
    def optimize_task_schedule(self, user_id: str, date: datetime) -> List[Dict[str, Any]]:
        """
        Optimize and reorder tasks for a specific date
        
        Args:
            user_id (str): User ID
            date (datetime): Date to optimize
            
        Returns:
            List of optimized tasks
        """
        try:
            if not self.llm:
                return []
            
            # Get tasks for the date
            tasks = self._get_tasks_for_date(user_id, date)
            if not tasks:
                return []
            
            # Get user profile for preferences
            user_profile = self._get_user_profile(user_id)
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a productivity optimization expert. Reorder and optimize the given tasks for maximum efficiency and well-being.
                
                Consider:
                - Task priorities and dependencies
                - Optimal timing for different types of work
                - Energy levels throughout the day
                - Need for breaks and variety
                
                Return the tasks in optimal order as JSON array, keeping the same format but adding "recommended_time" field:
                [
                    {
                        "id": "task_id",
                        "title": "Task title",
                        "estimated_duration_minutes": number,
                        "priority": 1-5,
                        "recommended_time": "HH:MM",
                        "reasoning": "Brief explanation for timing"
                    }
                ]"""),
                HumanMessage(content=f"""
                User's tasks for {date.strftime('%Y-%m-%d')}:
                {json.dumps(tasks, indent=2)}
                
                User preferences: {json.dumps(user_profile, indent=2) if user_profile else 'None available'}
                
                Optimize the task schedule for this day.
                """)
            ])
            
            response = self.llm(prompt.format_messages())
            
            try:
                optimized_tasks = json.loads(response.content)
                return optimized_tasks if isinstance(optimized_tasks, list) else tasks
            except json.JSONDecodeError:
                logger.error("Failed to parse optimized tasks JSON")
                return tasks
                
        except Exception as e:
            logger.error(f"Failed to optimize task schedule: {e}")
            return []
    
    def generate_progress_insights(self, user_id: str, goal_id: str) -> Dict[str, Any]:
        """
        Generate insights about goal progress
        
        Args:
            user_id (str): User ID
            goal_id (str): Goal ID
            
        Returns:
            Dict containing progress insights
        """
        try:
            if not self.llm:
                return {"error": "LLM not available"}
            
            # Get goal and task data
            goal = self._get_goal(user_id, goal_id)
            tasks = self._get_goal_tasks(user_id, goal_id)
            
            if not goal or not tasks:
                return {"error": "Goal or tasks not found"}
            
            # Calculate statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t["status"] == "completed"])
            overdue_tasks = len([t for t in tasks if t["status"] in ["pending", "in_progress"] 
                               and datetime.strptime(t["scheduled_date"], "%Y-%m-%d") < datetime.now()])
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a progress analysis expert. Analyze the goal progress and provide actionable insights.
                
                Return insights in JSON format:
                {
                    "overall_progress": "percentage or assessment",
                    "pace_assessment": "on-track|ahead|behind",
                    "key_achievements": ["achievement1", "achievement2"],
                    "areas_for_improvement": ["area1", "area2"],
                    "recommendations": ["recommendation1", "recommendation2"],
                    "motivation_message": "encouraging message"
                }"""),
                HumanMessage(content=f"""
                Goal: {goal["title"]}
                Target Date: {goal.get("target_completion_date", "Not set")}
                
                Task Statistics:
                - Total tasks: {total_tasks}
                - Completed tasks: {completed_tasks}
                - Overdue tasks: {overdue_tasks}
                - Progress: {goal.get("progress_percentage", 0)}%
                
                Recent task data:
                {json.dumps(tasks[-10:], indent=2)}  # Last 10 tasks
                
                Provide progress insights and recommendations.
                """)
            ])
            
            response = self.llm(prompt.format_messages())
            
            try:
                insights = json.loads(response.content)
                insights["statistics"] = {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "overdue_tasks": overdue_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                }
                return insights
            except json.JSONDecodeError:
                return {"error": "Failed to parse insights"}
                
        except Exception as e:
            logger.error(f"Failed to generate progress insights: {e}")
            return {"error": str(e)}
    
    def _get_existing_tasks(self, user_id: str, start_date: datetime, num_days: int) -> List[Dict[str, Any]]:
        """Get existing tasks for date range"""
        try:
            end_date = start_date + timedelta(days=num_days - 1)
            response = self.client.table("daily_tasks")\
                .select("scheduled_date, title, estimated_duration_minutes")\
                .eq("user_id", user_id)\
                .gte("scheduled_date", start_date.strftime("%Y-%m-%d"))\
                .lte("scheduled_date", end_date.strftime("%Y-%m-%d"))\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get existing tasks: {e}")
            return []
    
    def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            response = self.client.table("user_profiles")\
                .select("*")\
                .eq("id", user_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def _get_tasks_for_date(self, user_id: str, date: datetime) -> List[Dict[str, Any]]:
        """Get tasks for a specific date"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("scheduled_date", date.strftime("%Y-%m-%d"))\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get tasks for date: {e}")
            return []
    
    def _get_goal(self, user_id: str, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get goal information"""
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("id", goal_id)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get goal: {e}")
            return None
    
    def _get_goal_tasks(self, user_id: str, goal_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific goal"""
        try:
            response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("goal_id", goal_id)\
                .order("scheduled_date")\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get goal tasks: {e}")
            return []