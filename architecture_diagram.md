# Historical Facts MCP Server - Architecture & Plan

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           HISTORICAL FACTS MCP SERVER                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────────┐ │
│  │     AI APPLICATIONS     │    │              INTEGRATIONS                   │ │
│  │                         │    │                                             │ │
│  │  📱 ChatGPT Desktop     │◄──►│  🔌 MCP Protocol (STDIO)                   │ │
│  │  🤖 Claude Desktop      │    │  └─ JSON-RPC over stdin/stdout             │ │
│  │  🌐 Web Applications    │◄──►│  🌐 HTTP/REST API                          │ │
│  │  📊 Custom AI Tools     │    │  └─ FastAPI with CORS                      │ │
│  │  🔗 Other MCP Clients   │    │  📖 Interactive Documentation              │ │
│  └─────────────────────────┘    │  └─ Swagger UI at /docs                    │ │
│                                 └─────────────────────────────────────────────┘ │
│                                            ▲                                   │
│                                            │                                   │
│  ┌─────────────────────────────────────────┼─────────────────────────────────┐ │
│  │              MCP SERVER CORE            │                                 │ │
│  │                                         ▼                                 │ │
│  │  ┌─────────────────┐  ┌─────────────────────────────────────────────────┐ │ │
│  │  │   STDIO Mode    │  │                HTTP Mode                        │ │ │
│  │  │                 │  │                                                 │ │ │
│  │  │ ✅ MCP Protocol │  │ ✅ REST API Endpoints                          │ │ │
│  │  │ ✅ JSON-RPC     │  │ ✅ CORS Enabled                                │ │ │
│  │  │ ✅ Tool Support │  │ ✅ Health Monitoring                           │ │ │
│  │  │ ✅ Async I/O    │  │ ✅ Auto Documentation                          │ │ │
│  │  └─────────────────┘  │ ✅ MCP-Compatible Endpoints                    │ │ │
│  │                       └─────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────┼─────────────────────────────────┘ │
│                                            ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            CORE TOOLS                                      │ │
│  │                                                                             │ │
│  │  🎯 get_historical_facts                                                   │ │
│  │     └─ Get facts for specific dates (month/day)                           │ │
│  │     └─ Supports: events, births, deaths, holidays                         │ │
│  │     └─ Date validation & error handling                                    │ │
│  │                                                                             │ │
│  │  📅 get_todays_historical_facts                                            │ │
│  │     └─ Current date historical facts                                       │ │
│  │     └─ Dynamic date calculation                                            │ │
│  │     └─ Same filtering options                                              │ │
│  │                                                                             │ │
│  │  🎲 get_random_historical_fact                                             │ │
│  │     └─ Random date selection (1-28 days)                                  │ │
│  │     └─ Random event from results                                           │ │
│  │     └─ Surprise discovery feature                                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                            ▲                                   │
│                                            │                                   │
│  ┌─────────────────────────────────────────┼─────────────────────────────────┐ │
│  │                    DATA LAYER           │                                 │ │
│  │                                         ▼                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                  WIKIPEDIA API INTEGRATION                          │   │ │
│  │  │                                                                     │   │ │
│  │  │  🌐 api.wikimedia.org/feed/v1/wikipedia/en/onthisday/             │   │ │
│  │  │                                                                     │   │ │
│  │  │  📊 Endpoints:                                                      │   │ │
│  │  │     ├─ /all/MM/DD     - All event types                           │   │ │
│  │  │     ├─ /events/MM/DD  - Historical events                         │   │ │
│  │  │     ├─ /births/MM/DD  - Notable births                            │   │ │
│  │  │     ├─ /deaths/MM/DD  - Notable deaths                            │   │ │
│  │  │     └─ /holidays/MM/DD - Holidays & observances                   │   │ │
│  │  │                                                                     │   │ │
│  │  │  ⚡ Features:                                                        │   │ │
│  │  │     ├─ Rich metadata (descriptions, images, links)                │   │ │
│  │  │     ├─ Year information for historical context                    │   │ │
│  │  │     ├─ Wikipedia page extracts                                     │   │ │
│  │  │     ├─ Thumbnail images                                            │   │ │
│  │  │     └─ Direct Wikipedia links                                      │   │ │
│  │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────┼─────────────────────────────────┘ │
│                                            ▲                                   │
│                                            │                                   │
│  ┌─────────────────────────────────────────┼─────────────────────────────────┐ │
│  │                DATA PROCESSING          │                                 │ │
│  │                                         ▼                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    FORMATTING ENGINE                               │   │ │
│  │  │                                                                     │   │ │
│  │  │  📝 Text Formatting:                                                │   │ │
│  │  │     ├─ Markdown output with headers                                │   │ │
│  │  │     ├─ Emoji categorization (📅🎂⚰️🎉)                              │   │ │
│  │  │     ├─ Limited text length (300 chars)                            │   │ │
│  │  │     └─ Structured sections                                         │   │ │
│  │  │                                                                     │   │ │
│  │  │  🔍 Content Processing:                                             │   │ │
│  │  │     ├─ Event deduplication                                         │   │ │
│  │  │     ├─ Relevance filtering                                         │   │ │
│  │  │     ├─ Context extraction                                          │   │ │
│  │  │     └─ Link preservation                                           │   │ │
│  │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

                                  DEPLOYMENT LAYER
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  🌐 LIVE DEPLOYMENT                                                             │
│     └─ https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so      │
│                                                                                 │
│  📦 GITHUB REPOSITORY                                                           │
│     └─ https://github.com/oscar-fern-labs/historical-facts-mcp-server         │
│                                                                                 │
│  🔧 LOCAL DEVELOPMENT                                                           │
│     ├─ Virtual Environment (Python 3.10+)                                     │
│     ├─ Requirements: mcp, httpx, fastapi, uvicorn                             │
│     └─ Installation script provided                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Implementation Plan Status

### ✅ COMPLETED - Step 1: Backend Development

| Component | Status | Description |
|-----------|--------|-------------|
| 🔬 Research | ✅ Complete | MCP protocol, OpenAI ecosystem, Wikipedia API |
| 🏗️ Core MCP Server | ✅ Complete | STDIO-based server with 3 tools |
| 🌐 HTTP API Wrapper | ✅ Complete | FastAPI-based REST interface |
| 🔌 External Exposure | ✅ Complete | Live deployment with port exposure |
| 📚 Documentation | ✅ Complete | README, configs, installation guide |
| 🧪 Testing | ✅ Complete | API integration and endpoint testing |
| 📦 Repository | ✅ Complete | GitHub with clean commit history |
| 🎯 Artefact Registration | ✅ Complete | Both repo and live API registered |

### 🚧 PLANNED - Step 2: Frontend Development

| Component | Priority | Description |
|-----------|----------|-------------|
| 🖥️ Web Interface | High | Interactive web app for historical facts |
| 📱 Responsive Design | High | Mobile-friendly interface |
| 🎨 UI/UX Design | Medium | Clean, engaging design system |
| 🔍 Search Features | Medium | Date picker, category filters |
| 📊 Data Visualization | Low | Timeline view, category charts |
| 🔗 Share Features | Low | Social sharing, bookmark functionality |

### 🎁 PLANNED - Step 3: Final Integration

| Component | Priority | Description |
|-----------|----------|-------------|
| 🔄 Code Synchronization | High | Ensure all changes are in GitHub |
| 🧪 End-to-End Testing | High | Complete system verification |
| 📖 Final Documentation | High | Updated README with frontend |
| 🚀 Production Readiness | Medium | Performance optimization |

## 📊 Technical Specifications

### MCP Server Tools

#### 1. `get_historical_facts`
```json
{
  "name": "get_historical_facts",
  "description": "Get historical facts for a specific date",
  "inputSchema": {
    "type": "object",
    "properties": {
      "month": {"type": "integer", "minimum": 1, "maximum": 12},
      "day": {"type": "integer", "minimum": 1, "maximum": 31},
      "event_type": {
        "type": "string", 
        "enum": ["all", "events", "births", "deaths", "holidays"],
        "default": "all"
      }
    },
    "required": ["month", "day"]
  }
}
```

#### 2. `get_todays_historical_facts`
```json
{
  "name": "get_todays_historical_facts",
  "description": "Get historical facts for today's date",
  "inputSchema": {
    "type": "object",
    "properties": {
      "event_type": {
        "type": "string",
        "enum": ["all", "events", "births", "deaths", "holidays"],
        "default": "all"
      }
    }
  }
}
```

#### 3. `get_random_historical_fact`
```json
{
  "name": "get_random_historical_fact",
  "description": "Get a random historical fact from a random date",
  "inputSchema": {
    "type": "object",
    "properties": {
      "event_type": {
        "type": "string",
        "enum": ["all", "events", "births", "deaths", "holidays"],
        "default": "events"
      }
    }
  }
}
```

### HTTP API Endpoints

| Endpoint | Method | Description |
|----------|---------|------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/historical-facts/{month}/{day}` | GET | Historical facts by date |
| `/historical-facts/today` | GET | Today's historical facts |
| `/historical-facts/random` | GET | Random historical fact |
| `/docs` | GET | Interactive API documentation |
| `/mcp/call-tool` | POST | MCP-compatible tool calls |

## 🔗 Integration Patterns

### ChatGPT Desktop Integration
```json
{
  "mcpServers": {
    "historical-facts-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/historical_facts_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/historical-facts-mcp-server"
      }
    }
  }
}
```

### HTTP API Usage
```bash
# Get today's facts
curl https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so/historical-facts/today

# Get facts for specific date
curl https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so/historical-facts/12/25

# Get random fact
curl https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so/historical-facts/random
```

### MCP Tool Call
```bash
curl -X POST "/mcp/call-tool" -H "Content-Type: application/json" \
  -d '{"name": "get_historical_facts", "arguments": {"month": 7, "day": 4}}'
```

## 🎯 Success Metrics

### Functionality ✅
- [x] All 3 MCP tools working correctly
- [x] STDIO and HTTP modes operational
- [x] Wikipedia API integration stable
- [x] External accessibility confirmed
- [x] Documentation complete
- [x] Installation process verified

### Performance ✅
- [x] API response time < 2 seconds
- [x] Proper error handling
- [x] Input validation working
- [x] Memory usage optimized
- [x] Concurrent request support

### Integration ✅
- [x] MCP protocol compliance
- [x] JSON-RPC message handling
- [x] CORS enabled for web apps
- [x] GitHub repository accessible
- [x] Live deployment operational
