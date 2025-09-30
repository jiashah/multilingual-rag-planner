# 🎯 Multilingual RAG Planner

A powerful AI-driven goal planning and task management application that helps you break down your goals into actionable daily tasks. Features multilingual support, intelligent task generation using RAG (Retrieval Augmented Generation), and persistent user data storage.

## ✨ Features

### 🤖 AI-Powered Planning
- **Goal Analysis**: AI analyzes your goals for complexity, required skills, and potential obstacles
- **Smart Task Generation**: Automatically generates daily tasks based on your goals and context
- **RAG Integration**: Uses your uploaded documents for personalized task recommendations
- **Progress Insights**: AI-generated insights and recommendations for goal achievement

### 🌍 Multilingual Support
- **11+ Languages**: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Hindi, Arabic
- **Auto-Translation**: Automatic translation of goals, tasks, and AI responses
- **Language Detection**: Smart detection of input language
- **Localized UI**: Interface elements translated to your preferred language

### 📊 Comprehensive Dashboard
- **Progress Tracking**: Visual charts showing goal and task completion
- **Analytics**: Detailed statistics and trends
- **Calendar View**: Visual timeline of your tasks and deadlines
- **Activity Feed**: Recent activity and achievements

### 🔐 Secure Authentication
- **User Authentication**: Secure login/signup with Supabase Auth
- **Data Persistence**: All your data is saved and synced across devices
- **Privacy**: Your personal data is protected with row-level security

### 📱 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive UI**: Clean, user-friendly interface built with Streamlit
- **Real-time Updates**: Instant updates across all components

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Supabase account (free tier available)
- OpenAI API key (optional, for enhanced AI features)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multilingual-rag-planner.git
   cd multilingual-rag-planner
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration values
   ```

4. **Set up Supabase database**
   - Create a new Supabase project at [supabase.com](https://supabase.com)
   - Run the SQL schema in `database/schema.sql`
   - Update `.env` with your Supabase credentials

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

### Option 2: Docker Deployment

1. **Using Docker Compose (Recommended)**
   ```bash
   git clone https://github.com/yourusername/multilingual-rag-planner.git
   cd multilingual-rag-planner
   cp .env.example .env
   # Edit .env with your configuration
   docker-compose up --build
   ```

2. **Using Docker directly**
   ```bash
   docker build -t multilingual-rag-planner .
   docker run -p 8501:8501 --env-file .env multilingual-rag-planner
   ```

### Option 3: Deployment Script

Use the provided deployment script for automated setup:

```bash
chmod +x deploy.sh

# For local development
./deploy.sh local

# For Docker deployment
./deploy.sh docker-compose

# For production deployment
./deploy.sh production
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration (Optional - for enhanced AI features)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Application Settings
APP_NAME="Multilingual RAG Planner"
DEBUG_MODE=False
LOG_LEVEL=INFO

# Vector Database Settings
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDINGS_MODEL=all-MiniLM-L6-v2

# Task Generation Settings
MAX_DAILY_TASKS=10
PLANNING_HORIZON_DAYS=30

# Multilingual Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr,de,it,pt,zh,ja,ko,hi,ar
```

### Supabase Setup

1. **Create a new project** at [supabase.com](https://supabase.com)

2. **Run the database schema**:
   - Go to the SQL editor in your Supabase dashboard
   - Copy and run the content of `database/schema.sql`

3. **Configure authentication**:
   - Enable email/password authentication in Auth settings
   - Configure any additional auth providers if needed

4. **Set up Row Level Security (RLS)**:
   - RLS policies are included in the schema
   - Users can only access their own data

## 📋 Usage Guide

### Getting Started

1. **Sign Up**: Create a new account or log in with existing credentials
2. **Set Language**: Choose your preferred language from the sidebar
3. **Create Your First Goal**: Go to Goal Planner → Create New Goal
4. **Generate Tasks**: Use AI to automatically generate daily tasks
5. **Track Progress**: Monitor your progress on the Dashboard

### Creating Goals

1. Navigate to **Goal Planner** → **Create New Goal**
2. Fill in goal details:
   - **Title**: Clear, specific goal description
   - **Description**: Detailed explanation of what you want to achieve
   - **Category**: Choose from predefined categories
   - **Priority**: Set importance level (1-5)
   - **Target Date**: When you want to complete the goal
3. Enable **AI Analysis** for smart recommendations
4. Click **Create Goal**

### Managing Tasks

1. Go to **Task Manager** to view and manage your tasks
2. Use different tabs:
   - **Today's Tasks**: Focus on today's priorities
   - **Upcoming Tasks**: Plan for the week ahead
   - **All Tasks**: View and filter all tasks
   - **Create Task**: Manually add custom tasks

### Using AI Features

1. **Goal Analysis**: AI analyzes complexity and suggests approaches
2. **Task Generation**: Automatically creates relevant daily tasks
3. **Progress Insights**: Get AI-powered recommendations for improvement
4. **Document Upload**: Upload PDFs/documents for personalized recommendations

### Multilingual Features

1. **Language Selection**: Use the sidebar language selector
2. **Auto-Translation**: Content is automatically translated
3. **Mixed Languages**: Enter content in any language
4. **Language Detection**: System detects and handles multiple languages

## 🏗️ Architecture

### System Components

```
multilingual-rag-planner/
├── main.py                 # Main Streamlit application
├── auth/                   # Authentication system
│   └── auth_manager.py     # Supabase auth integration
├── components/             # UI components
│   ├── dashboard.py        # Main dashboard
│   ├── goal_planner.py     # Goal creation and management
│   └── task_manager.py     # Task management interface
├── rag/                    # RAG system
│   ├── rag_system.py       # Document processing and retrieval
│   └── goal_planner_agent.py # AI goal planning
├── database/               # Database operations
│   ├── supabase_client.py  # Database client
│   ├── operations.py       # CRUD operations
│   └── schema.sql          # Database schema
├── localization/           # Multilingual support
│   └── translator.py       # Translation system
└── utils/                  # Utilities
    └── logger.py           # Logging configuration
```

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI/ML**: OpenAI GPT, LangChain
- **Vector Database**: ChromaDB
- **Translation**: Google Translate API
- **Deployment**: Docker, Docker Compose

### Data Flow

1. **User Input** → Authentication & Language Detection
2. **Goal Creation** → AI Analysis & Database Storage  
3. **Task Generation** → RAG System → LLM → Database Storage
4. **Progress Tracking** → Analytics & Insights
5. **Multilingual** → Translation & Localization

## 🚀 Deployment Options

### 1. Local Development
Best for development and testing:
```bash
./deploy.sh local
```

### 2. Docker Deployment
Containerized deployment:
```bash
./deploy.sh docker-compose
```

### 3. Streamlit Cloud
Free cloud hosting:
```bash
./deploy.sh streamlit-cloud
# Then deploy via Streamlit Cloud dashboard
```

### 4. Production Deployment
For production environments:
```bash
./deploy.sh production
```

### 5. Cloud Platforms

**Heroku**:
1. Create a `Procfile`:
   ```
   web: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy using Heroku CLI

**Railway**:
1. Connect your GitHub repository
2. Add environment variables
3. Deploy automatically

**Google Cloud Run**:
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Goal creation with AI analysis
- [ ] Task generation and management
- [ ] Progress tracking and analytics
- [ ] Language switching and translation
- [ ] Document upload and RAG functionality

## 🔧 Development

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -m "Add feature"`
7. Push to branch: `git push origin feature-name`
8. Create a Pull Request

### Code Structure Guidelines

- Follow PEP 8 for Python code style
- Use type hints for function parameters and return values
- Add docstrings for all classes and functions
- Keep functions small and focused
- Use meaningful variable and function names

### Adding New Languages

1. Add language code to `supported_languages` in `translator.py`
2. Add UI translations to `ui_translations` dictionary
3. Test translation functionality
4. Update documentation

## 📊 API Documentation

### Database Operations

The application uses the `DatabaseOperations` class for all database interactions:

```python
from database.operations import db_ops

# Create a goal
goal_data = {
    "user_id": "user-uuid",
    "title": "Learn Python",
    "description": "Master Python programming",
    "category": "education",
    "priority": 4
}
goal = db_ops.create_goal(goal_data)

# Get user's goals
goals = db_ops.get_user_goals(user_id, status="active")

# Create tasks
task_data = {
    "user_id": "user-uuid",
    "goal_id": "goal-uuid",
    "title": "Read Python tutorial",
    "scheduled_date": "2024-01-15"
}
task = db_ops.create_task(task_data)
```

### Translation API

```python
from localization.translator import translator

# Detect language
language = translator.detect_language("Hello world")

# Translate text
translated = translator.translate_text("Hello", target_lang="es")

# Translate goal data
translated_goal = translator.translate_goal(goal_data, target_lang="fr")

# Get UI text
ui_text = translator.get_ui_text("dashboard", language="de")
```

### RAG System API

```python
from rag.rag_system import RAGSystem
from rag.goal_planner_agent import GoalPlannerAgent

# Initialize systems
rag = RAGSystem()
planner = GoalPlannerAgent()

# Process document
chunks = rag.process_document("document.pdf", "pdf")
rag.add_documents_to_vectorstore(chunks, user_id)

# Generate tasks
tasks = planner.generate_daily_tasks(goal, user_id, start_date, num_days=7)

# Get insights
insights = planner.generate_progress_insights(user_id, goal_id)
```

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Supabase connection failed"**
- Check your Supabase URL and API keys in `.env`
- Ensure your Supabase project is active
- Verify database schema is properly set up

**"OpenAI API error"**
- Check your OpenAI API key
- Verify you have sufficient API credits
- The app works without OpenAI, but with limited AI features

**"Translation not working"**
- Google Translate API might be rate-limited
- Check internet connection
- Try again after a few minutes

**"ChromaDB permission error"**
```bash
# Create directory with proper permissions
mkdir -p chroma_db
chmod 755 chroma_db
```

### Logs and Debugging

- Application logs are stored in the `logs/` directory
- Set `DEBUG_MODE=True` in `.env` for detailed logging
- Use `LOG_LEVEL=DEBUG` for maximum verbosity

### Performance Issues

- Increase server resources if handling many users
- Consider using OpenAI API for better performance
- Enable caching for frequently accessed data

## 🔒 Security

### Data Protection
- All user data is encrypted in transit and at rest
- Row Level Security (RLS) ensures users only access their own data
- Authentication tokens are securely managed by Supabase

### API Security
- API keys are stored as environment variables
- No sensitive data is logged
- Input validation prevents injection attacks

### Deployment Security
- Use HTTPS in production
- Keep dependencies updated
- Use secrets management for production deployments

## 📈 Monitoring and Analytics

### Application Metrics
- User registration and login rates
- Goal creation and completion rates
- Task completion statistics
- Feature usage analytics

### Performance Monitoring
- Response times
- Database query performance
- API usage and costs
- Error rates and logs

## 🛣️ Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Offline mode support
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Integration with calendar apps
- [ ] Voice input for tasks
- [ ] Habit tracking
- [ ] Goal templates library

### Long-term Vision
- Multi-platform support (web, mobile, desktop)
- AI coaching and mentoring
- Community features and goal sharing
- Advanced personalization
- Integration with productivity tools

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **Supabase** - For the backend infrastructure
- **LangChain** - For the RAG capabilities  
- **OpenAI** - For the AI language model
- **Google Translate** - For multilingual support
- **ChromaDB** - For vector storage

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/multilingual-rag-planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multilingual-rag-planner/discussions)
- **Email**: support@yourapp.com

## 🌟 Show Your Support

If this project helped you, please consider:
- Starring the repository ⭐
- Sharing with others 📢
- Contributing to the project 🤝
- Providing feedback 💬

---

**Happy Planning! 🎯**