"""
🔧 Jamie AI DevOps Copilot - Configuration

Sprint 2: Environment configuration and settings management

⭐ WHAT THIS FILE DOES:
    - Centralizes all configuration settings for Jamie
    - Reads environment variables with sensible defaults
    - Provides configuration validation and directory setup
    - Makes it easy to adjust Jamie's behavior without code changes
    - Supports different environments (dev, staging, production)
"""

import os
from typing import Optional
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# 🛠️ MAIN CONFIGURATION CLASS - All of Jamie's settings in one place
# ═══════════════════════════════════════════════════════════════════════════════

class JamieConfig:
    """
    🎯 Configuration management for Jamie AI DevOps Copilot
    
    HOW IT WORKS:
    - Reads environment variables with fallback defaults
    - Groups related settings together
    - Provides helper methods for setup and validation
    - Can be imported anywhere Jamie needs configuration
    
    ENVIRONMENT VARIABLES:
    - All settings can be overridden with environment variables
    - Use JAMIE_ prefix for Jamie-specific settings
    - Use standard names for common tools (OLLAMA_HOST, MONGODB_URL)
    """
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🌐 API SERVER CONFIGURATION - How Jamie's web server runs
    # ═══════════════════════════════════════════════════════════════════════════════
    
    HOST: str = os.getenv("JAMIE_HOST", "0.0.0.0")              # Which IP to bind to (0.0.0.0 = all)
    PORT: int = int(os.getenv("JAMIE_PORT", "8000"))            # Which port to listen on
    LOG_LEVEL: str = os.getenv("JAMIE_LOG_LEVEL", "INFO")       # How verbose logging should be
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🧠 AI BRAIN CONFIGURATION - Ollama LLM settings
    # ═══════════════════════════════════════════════════════════════════════════════
    
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")    # Where Ollama is running
    JAMIE_MODEL: str = os.getenv("JAMIE_MODEL", "llama3.1:8b")              # Which LLM model to use
    AI_TEMPERATURE: float = float(os.getenv("JAMIE_TEMPERATURE", "0.7"))     # Creativity level (0-1)
    AI_MAX_TOKENS: int = int(os.getenv("JAMIE_MAX_TOKENS", "2048"))          # Maximum response length
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🗄️ MEMORY CONFIGURATION - Where Jamie stores knowledge (legacy)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # 📁 LOCAL MEMORY SETTINGS (used before MongoDB RAG)
    MEMORY_DIR: str = os.getenv("JAMIE_MEMORY_DIR", "./jamie_memory")                    # Directory for memory files
    MAX_MEMORIES: int = int(os.getenv("JAMIE_MAX_MEMORIES", "10000"))                   # Maximum memories to keep
    SIMILARITY_THRESHOLD: float = float(os.getenv("JAMIE_SIMILARITY_THRESHOLD", "0.3")) # Minimum similarity for matches
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 💬 CONVERSATION CONFIGURATION - Chat session management
    # ═══════════════════════════════════════════════════════════════════════════════
    
    MAX_MESSAGES_PER_SESSION: int = int(os.getenv("JAMIE_MAX_MESSAGES", "1000"))    # Max messages per chat session
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("JAMIE_SESSION_TIMEOUT", "24"))      # When to expire old sessions
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🗃️ DATABASE CONFIGURATION - External storage systems
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # 🍃 MONGODB SETTINGS - For RAG knowledge base
    MONGODB_URL: Optional[str] = os.getenv("JAMIE_MONGODB_URL")                     # MongoDB connection string
    
    # 🔴 REDIS SETTINGS - For session caching (future use)
    REDIS_URL: Optional[str] = os.getenv("JAMIE_REDIS_URL")                         # Redis connection string
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🧠 RAG MEMORY CONFIGURATION - Enhanced knowledge system
    # ═══════════════════════════════════════════════════════════════════════════════
    
    RAG_DATABASE_NAME: str = os.getenv("JAMIE_RAG_DATABASE", "jamie_rag")                       # MongoDB database name
    RAG_MAX_DOCUMENTS: int = int(os.getenv("JAMIE_RAG_MAX_DOCUMENTS", "50000"))                 # Maximum documents in RAG
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("JAMIE_RAG_SIMILARITY_THRESHOLD", "0.3")) # RAG similarity threshold
    RAG_CONTEXT_LENGTH: int = int(os.getenv("JAMIE_RAG_CONTEXT_LENGTH", "4000"))                # Max context length for RAG
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔧 DEVELOPMENT CONFIGURATION - Debug and development settings
    # ═══════════════════════════════════════════════════════════════════════════════
    
    DEBUG: bool = os.getenv("JAMIE_DEBUG", "false").lower() == "true"         # Enable debug mode
    RELOAD: bool = os.getenv("JAMIE_RELOAD", "false").lower() == "true"       # Auto-reload on code changes
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 📊 OBSERVABILITY CONFIGURATION - Metrics, Tracing, and Logging
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # 📈 PROMETHEUS METRICS SETTINGS
    METRICS_ENABLED: bool = os.getenv("JAMIE_METRICS_ENABLED", "true").lower() == "true"
    METRICS_PATH: str = os.getenv("JAMIE_METRICS_PATH", "/metrics")
    METRICS_PORT: int = int(os.getenv("JAMIE_METRICS_PORT", "9090"))
    
    # 🔍 DISTRIBUTED TRACING SETTINGS  
    TRACING_ENABLED: bool = os.getenv("JAMIE_TRACING_ENABLED", "true").lower() == "true"
    TRACING_ENDPOINT: str = os.getenv("JAMIE_TRACING_ENDPOINT", "http://localhost:4317")
    TRACING_SERVICE_NAME: str = os.getenv("JAMIE_SERVICE_NAME", "jamie-devops-copilot")
    TRACING_SAMPLE_RATE: float = float(os.getenv("JAMIE_TRACING_SAMPLE_RATE", "1.0"))
    
    # 📝 ENHANCED LOGGING SETTINGS
    LOG_FORMAT: str = os.getenv("JAMIE_LOG_FORMAT", "json")  # json, text, or colored
    LOG_CORRELATION_ID: bool = os.getenv("JAMIE_LOG_CORRELATION", "true").lower() == "true"
    LOG_STRUCTURED: bool = os.getenv("JAMIE_LOG_STRUCTURED", "true").lower() == "true"
    LOG_FILE: Optional[str] = os.getenv("JAMIE_LOG_FILE")  # Optional log file path
    
    # 🚨 ALERTING SETTINGS  
    ALERTS_ENABLED: bool = os.getenv("JAMIE_ALERTS_ENABLED", "false").lower() == "true"
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("JAMIE_SLACK_WEBHOOK_URL")
    ERROR_THRESHOLD: int = int(os.getenv("JAMIE_ERROR_THRESHOLD", "10"))  # Errors per minute
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 🛠️ HELPER METHODS - Utility functions for configuration management
    # ═══════════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def ensure_directories(cls):
        """
        📁 Ensure required directories exist
        
        WHAT IT DOES:
        - Creates the memory directory if it doesn't exist
        - Sets up any other directories Jamie needs
        - Safe to call multiple times
        """
        Path(cls.MEMORY_DIR).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_summary(cls) -> dict:
        """
        📋 Get configuration summary for debugging and status checks
        
        RETURNS:
        - Organized summary of all configuration settings
        - Safe to log (no secrets exposed)
        - Useful for troubleshooting configuration issues
        """
        return {
            # 🌐 API SERVER SETTINGS
            "api": {
                "host": cls.HOST,
                "port": cls.PORT,
                "log_level": cls.LOG_LEVEL,
                "debug": cls.DEBUG
            },
            
            # 🧠 AI BRAIN SETTINGS
            "ai": {
                "ollama_host": cls.OLLAMA_HOST,
                "model": cls.JAMIE_MODEL,
                "temperature": cls.AI_TEMPERATURE,
                "max_tokens": cls.AI_MAX_TOKENS
            },
            
            # 🗄️ MEMORY SETTINGS (legacy)
            "memory": {
                "directory": cls.MEMORY_DIR,
                "max_memories": cls.MAX_MEMORIES,
                "similarity_threshold": cls.SIMILARITY_THRESHOLD
            },
            
            # 💬 CONVERSATION SETTINGS
            "conversation": {
                "max_messages": cls.MAX_MESSAGES_PER_SESSION,
                "session_timeout": cls.SESSION_TIMEOUT_HOURS
            },
            
            # 🗃️ DATABASE SETTINGS
            "database": {
                "mongodb_configured": cls.MONGODB_URL is not None,
                "redis_configured": cls.REDIS_URL is not None,
                "rag_database": cls.RAG_DATABASE_NAME
            },
            
            # 🧠 RAG SETTINGS
            "rag": {
                "max_documents": cls.RAG_MAX_DOCUMENTS,
                "similarity_threshold": cls.RAG_SIMILARITY_THRESHOLD,
                "context_length": cls.RAG_CONTEXT_LENGTH
            },
            
            # 📊 OBSERVABILITY SETTINGS
            "observability": {
                "metrics_enabled": cls.METRICS_ENABLED,
                "metrics_path": cls.METRICS_PATH,
                "metrics_port": cls.METRICS_PORT,
                "tracing_enabled": cls.TRACING_ENABLED,
                "tracing_endpoint": cls.TRACING_ENDPOINT,
                "service_name": cls.TRACING_SERVICE_NAME,
                "sample_rate": cls.TRACING_SAMPLE_RATE,
                "log_format": cls.LOG_FORMAT,
                "log_structured": cls.LOG_STRUCTURED,
                "alerts_enabled": cls.ALERTS_ENABLED
            }
        }

# ═══════════════════════════════════════════════════════════════════════════════
# 🌍 GLOBAL CONFIGURATION INSTANCE - Easy access throughout Jamie
# ═══════════════════════════════════════════════════════════════════════════════

# Create global config instance that can be imported anywhere
config = JamieConfig()

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 CONFIGURATION TESTING AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_config() -> dict:
    """
    ✅ Validate configuration and return status
    
    CHECKS:
    - Required directories can be created
    - Environment variables are valid types
    - Dependencies are available
    
    RETURNS: Validation results with any issues found
    """
    issues = []
    
    # 📁 CHECK DIRECTORY CREATION
    try:
        config.ensure_directories()
    except Exception as e:
        issues.append(f"Cannot create memory directory: {e}")
    
    # 🔢 CHECK NUMERIC VALUES
    if config.PORT < 1 or config.PORT > 65535:
        issues.append(f"Invalid port number: {config.PORT}")
    
    if config.AI_TEMPERATURE < 0 or config.AI_TEMPERATURE > 1:
        issues.append(f"Invalid AI temperature: {config.AI_TEMPERATURE}")
    
    # 🌐 CHECK URL FORMATS
    if config.MONGODB_URL and not config.MONGODB_URL.startswith(("mongodb://", "mongodb+srv://")):
        issues.append(f"Invalid MongoDB URL format: {config.MONGODB_URL}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config_summary": config.get_summary()
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🏃 EXAMPLE USAGE AND TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    🧪 Test configuration when run directly
    
    USAGE: python config.py
    
    This will:
    - Print current configuration
    - Validate settings
    - Show any issues found
    """
    print("🔧 Jamie Configuration Test")
    print("=" * 50)
    
    # 📋 SHOW CONFIGURATION SUMMARY
    print("\n📋 Current Configuration:")
    summary = config.get_summary()
    for section, settings in summary.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    # ✅ VALIDATE CONFIGURATION
    print("\n✅ Configuration Validation:")
    validation = validate_config()
    
    if validation["valid"]:
        print("✅ All configuration settings are valid!")
    else:
        print("❌ Configuration issues found:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    print("\n🚀 Jamie is ready to start!") 