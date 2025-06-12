# Jamie Migration to Google Gemini 2.0 Flash

This document describes the migration of Jamie AI DevOps Copilot from Ollama (llama3.1:8b) to Google Gemini 2.0 Flash.

## 🚀 What Changed

### Core AI Engine
- **Before**: Ollama with llama3.1:8b model via HTTP API calls
- **After**: Google Gemini 2.0 Flash via LangChain's `init_chat_model`

### Key Benefits
- ✨ **Better Performance**: Gemini 2.0 Flash offers faster response times
- 🧠 **Enhanced Intelligence**: More advanced reasoning and DevOps knowledge
- 🌐 **Cloud-Native**: No local GPU/CPU requirements for LLM inference
- 🔄 **Better Integration**: LangChain provides robust abstraction layer

## 📋 Prerequisites

### 1. Google API Key
You need a Google API key with access to Gemini 2.0 Flash:

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Ensure Gemini 2.0 Flash access is enabled

### 2. Updated Dependencies
New Python packages have been added:
```bash
pip install langchain==0.1.0 langchain-core==0.1.0 langchain-google-genai==1.0.0
```

## 🔧 Configuration

### Environment Variables
```bash
# Required: Google API key for Gemini
export GOOGLE_API_KEY="your-google-api-key-here"

# Updated: Model name
export JAMIE_MODEL="gemini-2.0-flash"

# Optional: Legacy Ollama support (if keeping for fallback)
export OLLAMA_HOST="http://localhost:11434"
```

### Docker Compose
Update your `.env` file:
```bash
GOOGLE_API_KEY=your-google-api-key-here
JAMIE_MODEL=gemini-2.0-flash
```

### Kubernetes Deployment
1. Create the Google API key secret:
```bash
kubectl create secret generic jamie-secrets \
  --from-literal=google-api-key=your-google-api-key-here \
  -n jamie
```

2. Update Helm values:
```yaml
jamie:
  config:
    ai:
      model: "gemini-2.0-flash"
      provider: "google_genai"
  secrets:
    googleApiKey: "your-google-api-key-here"
```

## 🔄 Migration Steps

### 1. Local Development
```bash
# 1. Set environment variables
export GOOGLE_API_KEY="your-api-key"
export JAMIE_MODEL="gemini-2.0-flash"

# 2. Install new dependencies
pip install -r requirements.txt

# 3. Test the migration
python repos/auto-devops/20-platform/services/langchain/test.py

# 4. Start Jamie
cd repos/auto-devops/20-platform/services/jamie
python -m uvicorn api.main:app --reload
```

### 2. Docker Deployment
```bash
# 1. Update environment file
echo "GOOGLE_API_KEY=your-api-key" >> .env
echo "JAMIE_MODEL=gemini-2.0-flash" >> .env

# 2. Rebuild and start
docker-compose build jamie
docker-compose up -d jamie
```

### 3. Kubernetes Deployment
```bash
# 1. Create secret
kubectl create secret generic jamie-secrets \
  --from-literal=google-api-key=your-google-api-key \
  -n jamie

# 2. Update Helm values and deploy
helm upgrade jamie ./helm/jamie -n jamie \
  --set jamie.secrets.googleApiKey=your-google-api-key
```

## 🧪 Testing the Migration

### 1. Health Check
```bash
curl http://localhost:8000/ai/status
```

Expected response should show:
```json
{
  "ai_brain": {
    "brain_available": true,
    "gemini_llm": {
      "available": true,
      "model": "gemini-2.0-flash"
    }
  }
}
```

### 2. Chat Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Jamie, how are you?",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

### 3. Verify Metrics
Check that metrics show the new model:
```bash
curl http://localhost:8000/metrics | grep gemini
```

## 🔄 Backward Compatibility

The migration maintains backward compatibility:

- **Ollama Infrastructure**: Can be kept running for other services
- **Configuration**: Legacy Ollama settings are preserved but not used
- **API**: All Jamie API endpoints remain unchanged
- **Features**: All existing functionality is preserved

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Not Working
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Test with curl
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models
```

#### 2. Import Errors
```bash
# Reinstall LangChain packages
pip uninstall langchain langchain-core langchain-google-genai
pip install langchain==0.1.0 langchain-core==0.1.0 langchain-google-genai==1.0.0
```

#### 3. Model Not Available
Check Jamie's logs for initialization errors:
```bash
docker-compose logs jamie | grep -i "gemini\|error"
```

### Rollback Plan

If you need to rollback to Ollama:

1. **Environment Variables**:
```bash
export JAMIE_MODEL="llama3.1:8b"
export OLLAMA_HOST="http://localhost:11434"
unset GOOGLE_API_KEY
```

2. **Restore brain.py**: 
```bash
git checkout HEAD~1 -- api/ai/brain.py
```

3. **Restart services**:
```bash
docker-compose restart jamie
```

## 📊 Performance Comparison

| Metric | Ollama (llama3.1:8b) | Gemini 2.0 Flash |
|--------|----------------------|-------------------|
| Response Time | 2-5 seconds | 0.5-2 seconds |
| CPU Usage | High (local inference) | Low (API calls) |
| Memory Usage | 8-16 GB | <1 GB |
| Model Quality | Good | Excellent |
| Cost | Free (local) | Pay-per-use |

## 🎯 Next Steps

After successful migration:

1. **Monitor Performance**: Track response times and error rates
2. **Optimize Prompts**: Leverage Gemini's enhanced capabilities
3. **Remove Ollama**: Consider removing Ollama infrastructure if not needed
4. **Update Documentation**: Update team documentation and runbooks

## 📚 Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google GenAI Integration](https://python.langchain.com/docs/integrations/chat/google_generative_ai)
- [Jamie Original Documentation](./README.md)

---

**Migration completed successfully! 🎉**

Jamie is now powered by Google Gemini 2.0 Flash and ready to provide enhanced DevOps assistance with improved performance and capabilities. 