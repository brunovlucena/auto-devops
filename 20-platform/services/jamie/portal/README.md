# 🤖 Jamie Chat Portal

**Sprint 4: ChatGPT-like interface for Jamie AI DevOps Copilot**

A modern, responsive chat interface built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

- **ChatGPT-style Interface** - Clean, intuitive chat experience
- **Real-time Communication** - WebSocket support with HTTP fallback
- **British Personality** - Jamie's charming DevOps wisdom
- **DevOps Integration** - Live data from Kubernetes, Prometheus, Loki
- **Syntax Highlighting** - Code blocks and logs beautifully rendered
- **Mobile Responsive** - Works perfectly on all devices
- **TypeScript** - Fully typed for better development experience

## 🛠️ Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React Markdown** - Markdown rendering with GFM support
- **Highlight.js** - Syntax highlighting for code blocks
- **Lucide React** - Beautiful, consistent icons
- **WebSocket** - Real-time communication

## 📦 Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

## 🔧 Environment Variables

```bash
# Jamie API Configuration
NEXT_PUBLIC_JAMIE_API_URL=http://localhost:8000
JAMIE_API_URL=http://localhost:8000
JAMIE_WS_URL=ws://localhost:8000
```

## 🚀 Usage

1. **Start Jamie's Backend**:
   ```bash
   cd ../  # Go to jamie directory
   python start_jamie.py
   ```

2. **Start the Portal**:
   ```bash
   npm run dev
   ```

3. **Open Browser**: Navigate to `http://localhost:3000`

## 💬 Chat Features

### **DevOps Questions**
- "How's my cluster doing?"
- "Show me recent errors"
- "What's the CPU usage?"
- "Any alerts firing?"

### **Real-time Features**
- Live WebSocket connection to Jamie
- Typing indicators
- Auto-scroll to latest messages
- Connection status monitoring

### **UI Features**
- Sidebar with system status
- Quick action buttons
- Message metadata (confidence, topics, intent)
- Syntax-highlighted code blocks
- Mobile-responsive design

## 🎨 Customization

### **Jamie's Colors**
```css
jamie: {
  primary: '#2563eb',      // British blue
  secondary: '#7c3aed',    // Purple accent
  success: '#059669',      // Green for success
  warning: '#d97706',      // Amber for warnings
  error: '#dc2626',        // Red for errors
  background: '#f8fafc',   // Light background
  surface: '#ffffff',      // White surface
  muted: '#64748b',        // Muted text
  border: '#e2e8f0',       // Border color
}
```

### **Typography**
- **Primary Font**: Inter (clean, modern)
- **Code Font**: Fira Code (programming ligatures)

## 📁 Project Structure

```
portal/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── globals.css     # Global styles
├── components/         # React components
│   ├── chat/          # Chat-specific components
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   └── layout/        # Layout components
│       ├── Header.tsx
│       └── Sidebar.tsx
├── lib/               # Utilities and API
│   ├── jamie-api.ts   # API client
│   └── utils.ts       # Helper functions
├── types/             # TypeScript types
│   └── chat.ts        # Chat-related types
└── public/            # Static assets
```

## 🔗 API Integration

The portal communicates with Jamie's FastAPI backend via:

- **HTTP API** - RESTful endpoints for chat, status, DevOps data
- **WebSocket** - Real-time bidirectional communication
- **Automatic Fallback** - Uses HTTP if WebSocket fails

### **Key Endpoints**
- `POST /chat` - Send message to Jamie
- `GET /health` - System health status
- `GET /mcp/status` - MCP server status
- `GET /devops/cluster/status` - Cluster overview
- `WS /ws/{user_id}` - WebSocket connection

## 🧪 Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Start production server
npm run start
```

## 🚀 Deployment

### **Production Build**
```bash
npm run build
```

### **Docker Deployment**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### **Environment Variables**
Set production URLs:
```bash
NEXT_PUBLIC_JAMIE_API_URL=https://jamie-api.yourdomain.com
JAMIE_API_URL=https://jamie-api.yourdomain.com
JAMIE_WS_URL=wss://jamie-api.yourdomain.com
```

## 🎯 Sprint 4 Goals

- ✅ **ChatGPT-style Interface** - Clean, modern chat UI
- ✅ **Real-time Streaming** - WebSocket communication
- ✅ **Conversation History** - Persistent chat sessions
- ✅ **Jamie's Personality** - British charm in responses
- ✅ **MCP Integration** - Live DevOps data
- ✅ **Syntax Highlighting** - Code and log rendering
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **TypeScript** - Fully typed codebase

## 🔮 Next: Sprint 5

**Slack Integration** - Bring Jamie to your team's Slack workspace!

---

**🤖 Jamie says**: "Brilliant! The chat portal is ready to go, mate! Pop open your browser and start asking me about your infrastructure - I've got all the answers with a proper British twist!" 🇬🇧 