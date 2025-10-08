# Historical Facts MCP Server - Step 1 Verification & Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ChatGPT Desktop  │  MCP Viewer  │  Direct HTTP  │  Web Frontend            │
│  (Custom Connector)│   (Testing)  │   (API Calls) │   (Browser)              │
└─────────────┬───────────────┬──────────────┬──────────────┬─────────────────┘
              │               │              │              │
              │ MCP Protocol  │ MCP Protocol │ HTTP/JSON    │ HTTP/REST
              │ over HTTP     │ over HTTP    │              │
              └───────────────┼──────────────┼──────────────┘
                              │              │              │
┌─────────────────────────────┼──────────────┼──────────────┼─────────────────┐
│                        TRANSPORT LAYER                     │                 │
├─────────────────────────────┼──────────────┼──────────────┼─────────────────┤
│                             │              │              │                 │
│  HTTPS External Access      │              │              │                 │
│  enhanced-apps-sdk-morphvm  │              │              │                 │
│  -87kmb6bw.http.cloud       │              │              │                 │
│  .morph.so                  │              │              │                 │
│                             │              │              │                 │
└─────────────────────────────┼──────────────┼──────────────┼─────────────────┘
                              │              │              │
┌─────────────────────────────┼──────────────┼──────────────┼─────────────────┐
│                        APPLICATION LAYER                   │                 │
├─────────────────────────────┼──────────────┼──────────────┼─────────────────┤
│                             │              │              │                 │
│  Enhanced Apps SDK Server   │              │              │  Frontend App   │
│  (Port 8005)               │              │              │  (Port 3000)    │
│                             │              │              │                 │
│  ┌─────────────────────────┐│              │              │  ┌─────────────┐│
│  │  MCP Protocol Handler  ││              │              │  │  React App  ││
│  │  /mcp endpoint         ││              │              │  │  Historical ││
│  │                        ││              │              │  │  Explorer   ││
│  │  • initialize          ││              │              │  └─────────────┘│
│  │  • tools/list          ││              │              │                 │
│  │  • tools/call          ││              │              │                 │
│  │  • resources/list      ││              │              │                 │
│  │  • resources/read      ││              │              │                 │
│  └─────────────────────────┘│              │              │                 │
│                             │              │              │                 │
│  ┌─────────────────────────┐│              │              │                 │
│  │  Apps SDK Components   ││              │              │                 │
│  │                        ││              │              │                 │
│  │  • Timeline Explorer   ││              │              │                 │
│  │  • Discovery Experience││              │              │                 │
│  │  • Interactive World   ││              │              │                 │
│  │    Map                 ││              │              │                 │
│  └─────────────────────────┘│              │              │                 │
│                             │              │              │                 │
│  ┌─────────────────────────┐│              │              │                 │
│  │  UI Component Server   ││              │              │                 │
│  │                        ││              │              │                 │
│  │  • /resources/{name}   ││              │              │                 │
│  │  • Static file serving ││              │              │                 │
│  │  • React/JSX templates ││              │              │                 │
│  └─────────────────────────┘│              │              │                 │
└─────────────────────────────┼──────────────┼──────────────┼─────────────────┘
                              │              │              │
┌─────────────────────────────┼──────────────┼──────────────┼─────────────────┐
│                         BUSINESS LOGIC LAYER              │                 │
├─────────────────────────────┼──────────────┼──────────────┼─────────────────┤
│                             │              │              │                 │
│  Historical Facts Engine    │              │              │  HTTP API       │
│                             │              │              │  Server         │
│  ┌─────────────────────────┐│              │              │  (Port 8000)    │
│  │  Tool Functions        ││              │              │                 │
│  │                        ││              │              │  ┌─────────────┐│
│  │  • historical_timeline ││              │              │  │  REST API   ││
│  │    _explorer()         ││              │              │  │  Wrapper    ││
│  │  • historical_discovery││              │              │  │             ││
│  │    _experience()       ││              │              │  │  • /health  ││
│  │  • historical_world    ││              │              │  │  • /today   ││
│  │    _map()              ││              │              │  │  • /random  ││
│  └─────────────────────────┘│              │              │  │  • /docs    ││
│                             │              │              │  └─────────────┘│
│  ┌─────────────────────────┐│              │              │                 │
│  │  State Management      ││              │              │                 │
│  │                        ││              │              │                 │
│  │  • User favorites      ││              │              │                 │
│  │  • User preferences    ││              │              │                 │
│  │  • Session context     ││              │              │                 │
│  └─────────────────────────┘│              │              │                 │
└─────────────────────────────┼──────────────┼──────────────┼─────────────────┘
                              │              │              │
┌─────────────────────────────┼──────────────┼──────────────┼─────────────────┐
│                          DATA LAYER                       │                 │
├─────────────────────────────┼──────────────┼──────────────┼─────────────────┤
│                             │              │              │                 │
│  Wikipedia On This Day API  │              │              │                 │
│                             │              │              │                 │
│  ┌─────────────────────────┐│              │              │                 │
│  │  External API Client   ││              │              │                 │
│  │                        ││              │              │                 │
│  │  • fetch_historical_   ││              │              │                 │
│  │    events()            ││              │              │                 │
│  │  • enrich_with_        ││              │              │                 │
│  │    wikipedia_data()    ││              │              │                 │
│  │  • generate_           ││              │              │                 │
│  │    recommendations()   ││              │              │                 │
│  └─────────────────────────┘│              │              │                 │
│                             │              │              │                 │
│  External Data Source:      │              │              │                 │
│  api.wikimedia.org/feed/v1/ │              │              │                 │
│  wikipedia/en/onthisday     │              │              │                 │
└─────────────────────────────┴──────────────┴──────────────┴─────────────────┘
```

## System Components Deep Dive

### 1. Enhanced Apps SDK MCP Server (Primary Backend)
**Location**: `enhanced_apps_sdk_server.py`
**Port**: 8005
**External URL**: `https://enhanced-apps-sdk-morphvm-87kmb6bw.http.cloud.morph.so/mcp`

**Capabilities**:
- Full MCP Protocol Implementation (JSON-RPC 2.0)
- OpenAI Apps SDK Feature Support
- 3 Interactive Tools with Rich UI Components
- State Management & Theme Integration
- Resource Serving for UI Components

### 2. Interactive Tools
#### A. Historical Timeline Explorer
- **Function**: `historical_timeline_explorer(month, day, event_type, view_mode)`
- **UI Component**: `historical-timeline-simple.html`
- **Features**: Interactive filtering, favorites, chronological display

#### B. Historical Discovery Experience  
- **Function**: `historical_discovery_experience(discovery_mode, focus_category, time_period)`
- **UI Component**: `historical-discovery.html`
- **Features**: Smart recommendations, carousels, themed exploration

#### C. Interactive World Map
- **Function**: `historical_world_map(month, day, map_style, marker_density, focus_region)`
- **UI Component**: `historical-map.html`
- **Features**: Geographic visualization, location clustering, regional focus

### 3. Apps SDK Features Demonstrated
- **State Persistence**: User favorites and preferences across sessions
- **Theme Integration**: Light/dark mode awareness via `window.openai` API
- **Interactive Actions**: Follow-up tool calls, user interactions
- **Rich UI Components**: React-based templates with proper JSX
- **Resource Management**: UI component serving and registration
- **Structured Content**: Metadata-rich responses with recommendations

### 4. Data Flow Architecture

```
Request Flow:
ChatGPT → HTTPS → MCP Server → Tool Function → Wikipedia API → Data Processing → Rich Response → UI Component → ChatGPT

Response Structure:
{
  "historical_data": [...],
  "recommendations": {...},
  "component_metadata": {...},
  "apps_sdk_metadata": {...}
}
```

## Research Foundation

### Apps SDK vs MCP Analysis
Based on user research and ChatGPT conversation:

1. **MCP Alone**: Basic tool calls, text responses
2. **Apps SDK**: Rich UI, interactive components, state management, distribution platform

### Implementation Strategy
1. **Built on MCP Foundation**: Proper protocol compliance
2. **Enhanced with Apps SDK**: Rich UI components and interactivity
3. **Comprehensive Features**: Timeline, discovery, mapping, recommendations
4. **Production Ready**: Error handling, logging, external accessibility

## Key Technical Decisions

1. **HTTP-based MCP**: Chosen over STDIO for ChatGPT Desktop compatibility
2. **React/JSX Components**: For rich interactive UI experiences
3. **Wikipedia API Integration**: Reliable historical data source
4. **Recommendation Engine**: Smart content discovery features
5. **Multi-layered Architecture**: Clean separation of concerns

This architecture demonstrates a complete transformation from basic MCP server to full Apps SDK implementation, showcasing all OpenAI Apps SDK capabilities while maintaining MCP protocol compliance.
