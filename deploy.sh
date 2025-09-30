#!/bin/bash

# Multilingual RAG Planner Deployment Script
# Supports local, Docker, and cloud deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual configuration values!"
            exit 1
        else
            print_error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Validate required environment variables
validate_env() {
    print_step "Validating environment variables..."
    
    required_vars=("SUPABASE_URL" "SUPABASE_ANON_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_error "Please set these in your .env file"
        exit 1
    fi
    
    print_message "Environment variables validated successfully"
}

# Local development deployment
deploy_local() {
    print_step "Starting local development deployment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_step "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_step "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p logs chroma_db
    
    # Run the application
    print_step "Starting Streamlit application..."
    streamlit run main.py --server.port=8501
}

# Docker deployment
deploy_docker() {
    print_step "Starting Docker deployment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Build Docker image
    print_step "Building Docker image..."
    docker build -t multilingual-rag-planner .
    
    # Run Docker container
    print_step "Starting Docker container..."
    docker run --rm -p 8501:8501 --env-file .env multilingual-rag-planner
}

# Docker Compose deployment
deploy_docker_compose() {
    print_step "Starting Docker Compose deployment..."
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Load environment variables
    export $(cat .env | xargs)
    
    # Start services
    print_step "Starting services with Docker Compose..."
    docker-compose up --build
}

# Streamlit Cloud deployment preparation
prepare_streamlit_cloud() {
    print_step "Preparing for Streamlit Cloud deployment..."
    
    # Create streamlit config directory
    mkdir -p .streamlit
    
    # Create config.toml
    cat > .streamlit/config.toml << EOF
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF
    
    # Create secrets.toml template
    cat > .streamlit/secrets.toml.example << EOF
# Supabase Configuration
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_ANON_KEY = "your_supabase_anon_key"
SUPABASE_SERVICE_ROLE_KEY = "your_supabase_service_role_key"

# OpenAI Configuration
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-3.5-turbo"

# Application Settings
APP_NAME = "Multilingual RAG Planner"
DEBUG_MODE = false

# Vector Database Settings
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"

# Task Generation Settings
MAX_DAILY_TASKS = 10
PLANNING_HORIZON_DAYS = 30

# Multilingual Settings
DEFAULT_LANGUAGE = "en"
EOF
    
    print_message "Streamlit Cloud configuration created!"
    print_warning "Please copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and update with your actual values"
    print_message "Then push your code to GitHub and deploy via Streamlit Cloud dashboard"
}

# Production deployment with additional configurations
deploy_production() {
    print_step "Preparing production deployment..."
    
    # Set production environment
    export DEBUG_MODE=false
    export LOG_LEVEL=WARNING
    
    # Use Docker Compose with production overrides
    if [ -f "docker-compose.prod.yml" ]; then
        print_step "Using production Docker Compose configuration..."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
    else
        print_step "Using standard Docker Compose configuration..."
        deploy_docker_compose &
    fi
    
    print_message "Production deployment started!"
    print_message "Application will be available at http://localhost:8501"
}

# Health check function
health_check() {
    print_step "Performing health check..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health 2>/dev/null; then
            print_message "Application is healthy!"
            return 0
        fi
        
        print_message "Attempt $attempt/$max_attempts - waiting for application to start..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Application failed to start or is not responding"
    return 1
}

# Cleanup function
cleanup() {
    print_step "Cleaning up..."
    
    # Stop Docker containers
    docker-compose down 2>/dev/null || true
    
    # Remove unused Docker images
    docker image prune -f 2>/dev/null || true
    
    print_message "Cleanup completed"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local                 Deploy for local development"
    echo "  docker                Deploy using Docker"
    echo "  docker-compose        Deploy using Docker Compose"
    echo "  streamlit-cloud       Prepare for Streamlit Cloud deployment"
    echo "  production           Deploy for production"
    echo "  health-check         Check application health"
    echo "  cleanup              Clean up Docker resources"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 docker-compose"
    echo "  $0 production"
}

# Main execution
main() {
    # Check if running in correct directory
    if [ ! -f "main.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Load environment variables if .env exists
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
    fi
    
    case "${1:-local}" in
        "local")
            check_env_file
            validate_env
            deploy_local
            ;;
        "docker")
            check_env_file
            validate_env
            deploy_docker
            ;;
        "docker-compose")
            check_env_file
            validate_env
            deploy_docker_compose
            ;;
        "streamlit-cloud")
            prepare_streamlit_cloud
            ;;
        "production")
            check_env_file
            validate_env
            deploy_production
            ;;
        "health-check")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"