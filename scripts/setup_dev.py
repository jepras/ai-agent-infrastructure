#!/usr/bin/env python3
"""
Development environment setup script for AI Email Processor
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd, capture_output=True, text=True, check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None


def create_env_file():
    """Create .env file from example"""
    if not os.path.exists(".env"):
        print("📝 Creating .env file from env.example...")
        if os.path.exists("env.example"):
            with open("env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("✅ Created .env file")
        else:
            print("❌ env.example not found")


def setup_backend():
    """Setup Python backend"""
    print("\n🐍 Setting up Python backend...")

    # Create virtual environment
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command("python3 -m venv venv")

    # Install dependencies
    print("Installing Python dependencies...")
    run_command("pip install -r requirements.txt")

    # Create backend directories
    backend_dirs = [
        "backend/app",
        "backend/app/auth",
        "backend/app/api",
        "backend/app/services",
        "backend/app/models",
        "backend/app/core",
        "backend/app/utils",
        "migrations",
        "migrations/versions",
    ]

    for dir_path in backend_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        Path(f"{dir_path}/__init__.py").touch(exist_ok=True)


def setup_frontend():
    """Setup Next.js frontend"""
    print("\n⚛️ Setting up Next.js frontend...")

    # Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd="frontend")

    # Create frontend directories
    frontend_dirs = [
        "frontend/src/components",
        "frontend/src/lib",
        "frontend/src/lib/auth",
        "frontend/src/lib/api",
        "frontend/src/lib/hooks",
        "frontend/src/lib/types",
        "frontend/src/lib/utils",
        "frontend/src/app/auth",
        "frontend/src/app/dashboard",
        "frontend/src/app/setup",
    ]

    for dir_path in frontend_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def setup_database():
    """Setup database migrations"""
    print("\n🗄️ Setting up database...")

    # Initialize Alembic
    if not os.path.exists("alembic.ini"):
        print("Initializing Alembic...")
        run_command("alembic init migrations")

    # Create initial migration
    print("Creating initial migration...")
    run_command("alembic revision --autogenerate -m 'Initial schema'")


def main():
    """Main setup function"""
    print("🚀 Setting up AI Email Processor development environment...")

    # Check prerequisites
    print("Checking prerequisites...")
    if not run_command("python3 --version"):
        print("❌ Python 3 is required")
        sys.exit(1)

    if not run_command("node --version"):
        print("❌ Node.js is required")
        sys.exit(1)

    if not run_command("npm --version"):
        print("❌ npm is required")
        sys.exit(1)

    # Setup environment
    create_env_file()

    # Setup backend
    setup_backend()

    # Setup frontend
    setup_frontend()

    # Setup database
    setup_database()

    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your credentials")
    print("2. Set up Railway project and add PostgreSQL")
    print("3. Configure OAuth applications (Outlook, Pipedrive)")
    print("4. Run 'cd backend && uvicorn main:app --reload' to start backend")
    print("5. Run 'cd frontend && npm run dev' to start frontend")
    print("\n📚 See README.md for detailed setup instructions")


if __name__ == "__main__":
    main()
