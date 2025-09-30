"""
Goal Planner Component - Create and manage goals with AI assistance
"""

import streamlit as st
from datetime import datetime, timedelta
from database.supabase_client import supabase_client
from rag.goal_planner_agent import GoalPlannerAgent
from utils.logger import setup_logger

logger = setup_logger("goal_planner")

class GoalPlanner:
    def __init__(self):
        self.client = supabase_client.client
        self.planner_agent = GoalPlannerAgent()
    
    def render(self):
        """Render the goal planner page"""
        st.header("🎯 Goal Planner")
        
        user_id = st.session_state.user_id
        
        # Navigation tabs
        tab1, tab2, tab3 = st.tabs(["Create New Goal", "My Goals", "AI Insights"])
        
        with tab1:
            self._render_create_goal_form(user_id)
        
        with tab2:
            self._render_goals_list(user_id)
        
        with tab3:
            self._render_ai_insights(user_id)
    
    def _render_create_goal_form(self, user_id: str):
        """Render goal creation form"""
        st.subheader("✨ Create a New Goal")
        
        with st.form("create_goal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Goal Title *", placeholder="e.g., Learn Spanish fluently")
                description = st.text_area("Description", placeholder="Detailed description of your goal...")
                category = st.selectbox("Category", [
                    "career", "health", "education", "personal", 
                    "finance", "relationship", "hobby", "other"
                ])
                priority = st.slider("Priority", 1, 5, 3, help="1=Low, 5=High")
            
            with col2:
                target_date = st.date_input(
                    "Target Completion Date",
                    value=datetime.now() + timedelta(days=90),
                    min_value=datetime.now().date()
                )
                
                # AI Analysis toggle
                use_ai_analysis = st.checkbox("Use AI Analysis", value=True, 
                                            help="Get AI-powered insights and suggestions for your goal")
                
                st.markdown("**AI Features:**")
                st.write("- Goal complexity analysis")
                st.write("- Milestone generation")
                st.write("- Task recommendations")
                st.write("- Progress tracking")
            
            submitted = st.form_submit_button("Create Goal", type="primary")
            
            if submitted:
                if not title:
                    st.error("Please enter a goal title")
                else:
                    self._create_goal(user_id, {
                        "title": title,
                        "description": description,
                        "category": category,
                        "priority": priority,
                        "target_completion_date": target_date.strftime("%Y-%m-%d"),
                        "use_ai_analysis": use_ai_analysis
                    })
    
    def _create_goal(self, user_id: str, goal_data: dict):
        """Create a new goal with optional AI analysis"""
        try:
            # AI analysis if requested
            ai_analysis = None
            if goal_data["use_ai_analysis"]:
                with st.spinner("🤖 Analyzing your goal with AI..."):
                    ai_analysis = self.planner_agent.analyze_goal(
                        f"{goal_data['title']} - {goal_data['description']}", 
                        user_id
                    )
                
                if "error" in ai_analysis:
                    st.warning(f"AI analysis unavailable: {ai_analysis['error']}")
                    ai_analysis = None
            
            # Prepare goal for database
            goal_record = {
                "user_id": user_id,
                "title": goal_data["title"],
                "description": goal_data["description"],
                "category": goal_data["category"],
                "priority": goal_data["priority"],
                "target_completion_date": goal_data["target_completion_date"],
                "status": "active",
                "progress_percentage": 0
            }
            
            # Add AI analysis results if available
            if ai_analysis and "error" not in ai_analysis:
                # Update category and priority based on AI analysis
                if ai_analysis.get("category"):
                    goal_record["category"] = ai_analysis["category"]
                if ai_analysis.get("priority"):
                    goal_record["priority"] = ai_analysis["priority"]
            
            # Insert goal into database
            response = self.client.table("goals").insert(goal_record).execute()
            
            if response.data:
                goal_id = response.data[0]["id"]
                st.success("🎉 Goal created successfully!")
                
                # Show AI analysis results
                if ai_analysis and "error" not in ai_analysis:
                    st.info("🤖 AI Analysis Results:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Estimated Duration:** {ai_analysis.get('estimated_duration_weeks', 'N/A')} weeks")
                        st.write(f"**Complexity:** {ai_analysis.get('complexity', 'N/A').title()}")
                        st.write(f"**Recommended Approach:** {ai_analysis.get('recommended_approach', 'N/A')}")
                    
                    with col2:
                        if ai_analysis.get("required_skills"):
                            st.write("**Required Skills:**")
                            for skill in ai_analysis["required_skills"]:
                                st.write(f"• {skill}")
                        
                        if ai_analysis.get("potential_obstacles"):
                            st.write("**Potential Obstacles:**")
                            for obstacle in ai_analysis["potential_obstacles"]:
                                st.write(f"⚠️ {obstacle}")
                
                # Generate initial tasks
                if st.button("🚀 Generate Initial Tasks"):
                    self._generate_initial_tasks(user_id, response.data[0])
                    
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            st.error("Failed to create goal. Please try again.")
    
    def _generate_initial_tasks(self, user_id: str, goal: dict):
        """Generate initial daily tasks for the goal"""
        try:
            with st.spinner("🤖 Generating initial tasks..."):
                tasks = self.planner_agent.generate_daily_tasks(
                    goal, user_id, datetime.now(), num_days=7
                )
            
            if tasks:
                # Insert tasks into database
                for task in tasks:
                    self.client.table("daily_tasks").insert(task).execute()
                
                st.success(f"✅ Generated {len(tasks)} tasks for the next 7 days!")
                
                # Show first few tasks
                st.write("**First few tasks:**")
                for task in tasks[:3]:
                    st.write(f"📅 {task['scheduled_date']}: **{task['title']}**")
                    st.write(f"   📝 {task['description']}")
                    st.write(f"   ⏱️ {task['estimated_duration_minutes']} minutes")
            else:
                st.warning("Could not generate tasks. You can create them manually in the Task Manager.")
                
        except Exception as e:
            logger.error(f"Failed to generate initial tasks: {e}")
            st.error("Failed to generate initial tasks.")
    
    def _render_goals_list(self, user_id: str):
        """Render user's goals list"""
        st.subheader("📋 Your Goals")
        
        try:
            # Get user's goals
            response = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            goals = response.data if response.data else []
            
            if not goals:
                st.info("No goals created yet. Create your first goal in the 'Create New Goal' tab!")
                return
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["all", "active", "completed", "paused", "cancelled"])
            with col2:
                category_filter = st.selectbox("Filter by Category", 
                    ["all"] + list(set(g["category"] for g in goals if g.get("category"))))
            with col3:
                sort_by = st.selectbox("Sort by", ["created_at", "priority", "progress", "target_date"])
            
            # Apply filters
            filtered_goals = goals
            if status_filter != "all":
                filtered_goals = [g for g in filtered_goals if g["status"] == status_filter]
            if category_filter != "all":
                filtered_goals = [g for g in filtered_goals if g.get("category") == category_filter]
            
            # Display goals
            for goal in filtered_goals:
                self._render_goal_card(goal, user_id)
                
        except Exception as e:
            logger.error(f"Failed to fetch goals: {e}")
            st.error("Failed to load goals.")
    
    def _render_goal_card(self, goal: dict, user_id: str):
        """Render a single goal card"""
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # Goal title and description
                status_emoji = {"active": "🔥", "completed": "✅", "paused": "⏸️", "cancelled": "❌"}
                st.write(f"{status_emoji.get(goal['status'], '📋')} **{goal['title']}**")
                if goal.get("description"):
                    st.write(goal["description"][:100] + "..." if len(goal["description"]) > 100 else goal["description"])
            
            with col2:
                # Progress bar
                progress = goal.get("progress_percentage", 0)
                st.metric("Progress", f"{progress}%")
                st.progress(progress / 100)
            
            with col3:
                # Priority and category
                priority_stars = "⭐" * goal.get("priority", 3)
                st.write(f"**Priority:** {priority_stars}")
                st.write(f"**Category:** {goal.get('category', 'N/A').title()}")
            
            with col4:
                # Action buttons
                if st.button(f"📊 View Details", key=f"view_{goal['id']}"):
                    self._show_goal_details(goal, user_id)
                
                if goal["status"] == "active":
                    if st.button(f"📝 Generate Tasks", key=f"gen_{goal['id']}"):
                        self._generate_weekly_tasks(goal, user_id)
            
            # Target date and timeline
            if goal.get("target_completion_date"):
                target_date = datetime.strptime(goal["target_completion_date"], "%Y-%m-%d")
                days_left = (target_date - datetime.now()).days
                
                if days_left > 0:
                    st.write(f"🎯 Target: {goal['target_completion_date']} ({days_left} days left)")
                elif days_left == 0:
                    st.write("🎯 Target: Today!")
                else:
                    st.write(f"🎯 Target: {goal['target_completion_date']} ({abs(days_left)} days overdue)")
            
            st.markdown("---")
    
    def _show_goal_details(self, goal: dict, user_id: str):
        """Show detailed view of a goal"""
        st.subheader(f"📋 Goal Details: {goal['title']}")
        
        # Basic information
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Description:** {goal.get('description', 'No description')}")
            st.write(f"**Category:** {goal.get('category', 'N/A').title()}")
            st.write(f"**Priority:** {'⭐' * goal.get('priority', 3)}")
            st.write(f"**Status:** {goal['status'].title()}")
        
        with col2:
            st.write(f"**Created:** {goal['created_at'][:10]}")
            st.write(f"**Target Date:** {goal.get('target_completion_date', 'Not set')}")
            st.write(f"**Progress:** {goal.get('progress_percentage', 0)}%")
        
        # Get goal statistics
        try:
            task_response = self.client.table("daily_tasks")\
                .select("*")\
                .eq("goal_id", goal["id"])\
                .execute()
            
            tasks = task_response.data if task_response.data else []
            completed_tasks = len([t for t in tasks if t["status"] == "completed"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", len(tasks))
            with col2:
                st.metric("Completed Tasks", completed_tasks)
            with col3:
                completion_rate = (completed_tasks / len(tasks) * 100) if tasks else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"Failed to get goal statistics: {e}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Update Goal"):
                st.session_state[f"edit_goal_{goal['id']}"] = True
        
        with col2:
            if goal["status"] == "active" and st.button("⏸️ Pause Goal"):
                self._update_goal_status(goal["id"], "paused")
                st.rerun()
        
        with col3:
            if st.button("🤖 AI Insights"):
                self._show_ai_insights_for_goal(user_id, goal["id"])
    
    def _generate_weekly_tasks(self, goal: dict, user_id: str):
        """Generate tasks for the next week"""
        try:
            with st.spinner("🤖 Generating tasks for next 7 days..."):
                tasks = self.planner_agent.generate_daily_tasks(
                    goal, user_id, datetime.now(), num_days=7
                )
            
            if tasks:
                # Insert tasks into database
                inserted = 0
                for task in tasks:
                    try:
                        self.client.table("daily_tasks").insert(task).execute()
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"Task insertion failed: {e}")
                        continue
                
                if inserted > 0:
                    st.success(f"✅ Generated {inserted} new tasks!")
                else:
                    st.warning("No new tasks were created (might already exist)")
            else:
                st.warning("Could not generate tasks at this time.")
                
        except Exception as e:
            logger.error(f"Failed to generate weekly tasks: {e}")
            st.error("Failed to generate tasks.")
    
    def _update_goal_status(self, goal_id: str, new_status: str):
        """Update goal status"""
        try:
            self.client.table("goals")\
                .update({"status": new_status})\
                .eq("id", goal_id)\
                .execute()
            
            st.success(f"Goal status updated to {new_status}")
        except Exception as e:
            logger.error(f"Failed to update goal status: {e}")
            st.error("Failed to update goal status.")
    
    def _render_ai_insights(self, user_id: str):
        """Render AI insights page"""
        st.subheader("🤖 AI-Powered Insights")
        
        # Get active goals
        try:
            response = self.client.table("goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .execute()
            
            active_goals = response.data if response.data else []
            
            if not active_goals:
                st.info("No active goals found. Create some goals to get AI insights!")
                return
            
            # Goal selector
            goal_titles = {goal["id"]: goal["title"] for goal in active_goals}
            selected_goal_id = st.selectbox(
                "Select a goal for insights:",
                options=list(goal_titles.keys()),
                format_func=lambda x: goal_titles[x]
            )
            
            if selected_goal_id and st.button("🔍 Generate Insights"):
                self._show_ai_insights_for_goal(user_id, selected_goal_id)
                
        except Exception as e:
            logger.error(f"Failed to load goals for insights: {e}")
            st.error("Failed to load goals.")
    
    def _show_ai_insights_for_goal(self, user_id: str, goal_id: str):
        """Show AI insights for a specific goal"""
        try:
            with st.spinner("🤖 Generating AI insights..."):
                insights = self.planner_agent.generate_progress_insights(user_id, goal_id)
            
            if "error" in insights:
                st.error(f"Could not generate insights: {insights['error']}")
                return
            
            # Display insights
            st.success("🤖 AI Insights Generated!")
            
            # Overall progress
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Progress", insights.get("overall_progress", "N/A"))
                st.metric("Pace Assessment", insights.get("pace_assessment", "N/A").title())
            
            with col2:
                if "statistics" in insights:
                    stats = insights["statistics"]
                    st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
                    st.metric("Total Tasks", stats['total_tasks'])
            
            # Key insights
            if insights.get("key_achievements"):
                st.subheader("🎉 Key Achievements")
                for achievement in insights["key_achievements"]:
                    st.write(f"• {achievement}")
            
            if insights.get("areas_for_improvement"):
                st.subheader("🎯 Areas for Improvement")
                for area in insights["areas_for_improvement"]:
                    st.write(f"• {area}")
            
            if insights.get("recommendations"):
                st.subheader("💡 Recommendations")
                for rec in insights["recommendations"]:
                    st.write(f"• {rec}")
            
            # Motivation message
            if insights.get("motivation_message"):
                st.info(f"💪 {insights['motivation_message']}")
                
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            st.error("Failed to generate AI insights.")