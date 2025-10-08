# Historical Facts MCP Server 📅

A fun and engaging MCP (Model Context Protocol) server that provides fascinating historical facts from events that happened on the same date in history! Perfect for integration with ChatGPT, Claude, and other AI applications.

## 🚀 Features

- **📅 Date-Specific Facts**: Get historical events, births, deaths, and holidays for any specific date
- **🎯 Today's History**: Quick access to what happened on today's date throughout history
- **🎲 Random Facts**: Discover surprising historical events from random dates
- **🌟 Rich Content**: Detailed descriptions, context, and Wikipedia links for deeper exploration
- **⚡ Fast & Reliable**: Uses Wikipedia's robust "On This Day" API
- **🔧 Easy Integration**: Simple MCP protocol for seamless AI app integration

## 🎨 ChatGPT Apps SDK Integration

This server now includes **full ChatGPT Apps SDK compatibility** with rich interactive components:

### 🕰️ Timeline Explorer
- Interactive historical timeline with filtering and favorites
- Beautiful gradient header with statistics
- Event cards with year badges and categories
- JavaScript filtering functionality (All, Events, Births, Deaths, Holidays)

### 🌟 Discovery Experience  
- Immersive historical discovery with smart recommendations
- Animated discovery cards with staggered appearance
- Color-coded year badges and category labels
- Diverse content from different time periods

### 🗺️ World Map Visualization
- Interactive world map with geographic markers
- Historical event locations plotted on map
- Color-coded legend for different event types
- Professional styling with teal/green theme

**✅ All components render properly in ChatGPT with embedded data templates, bypassing current Apps SDK limitations.**

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/oscar-fern-labs/historical-facts-mcp-server.git
cd historical-facts-mcp-server

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Test the Installation

```bash
python test_api.py
```

## 🎯 Available Tools

### 1. `get_historical_facts`
Get historical facts for a specific date.

**Parameters:**
- `month` (required): Month (1-12)
- `day` (required): Day (1-31)  
- `event_type` (optional): Type of events ("all", "events", "births", "deaths", "holidays")

### 2. `get_todays_historical_facts`
Get historical facts for today's date.

**Parameters:**
- `event_type` (optional): Type of events ("all", "events", "births", "deaths", "holidays")

### 3. `get_random_historical_fact`
Get a random historical fact from a random date.

**Parameters:**
- `event_type` (optional): Type of events ("events", "births", "deaths", "holidays")

## 🔌 Running the Server

### For ChatGPT Desktop (Recommended)

The server runs in STDIO mode for MCP protocol compatibility:

```bash
python historical_facts_server.py
```

### Configuration for ChatGPT

Add this configuration to your ChatGPT Desktop MCP settings:

```json
{
  "mcpServers": {
    "historical-facts": {
      "command": "python",
      "args": ["/path/to/historical-facts-mcp-server/historical_facts_server.py"],
      "env": {}
    }
  }
}
```

## 🌟 Example Usage

Once connected to your AI application, you can ask questions like:

- "What happened on January 15th in history?"
- "Tell me about historical events on my birthday (March 21)"
- "Give me a random historical fact"
- "What notable births occurred on July 4th?"
- "Show me historical deaths on December 25th"

## 📝 Example Response

```markdown
# Historical Facts for 1/15

## 📅 Historical Events

**2009**: US Airways Flight 1549 struck a flock of Canada geese during its climb out from New York City and made an emergency landing in the Hudson River.

*US Airways Flight 1549*: US Airways Flight 1549 was a regularly scheduled US Airways flight from New York City's LaGuardia Airport to Charlotte and Seattle...

## 🎂 Notable Births

🎂 **1929**: Martin Luther King Jr., American minister and activist, was born.

*About Martin Luther King Jr.*: Martin Luther King Jr. was an American Baptist minister and activist who became the most visible spokesperson...
```

## 🔧 Development

### Running Tests

```bash
python test_api.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 API Reference

The server uses Wikipedia's "On This Day" API:
- Base URL: `https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/`
- Endpoints: `/all/MM/DD`, `/events/MM/DD`, `/births/MM/DD`, `/deaths/MM/DD`, `/holidays/MM/DD`

## 🔧 Technical Implementation

### Server Architecture
- **Enhanced MCP Server**: `enhanced_apps_sdk_server_fixed.py` - ChatGPT-compatible version with embedded HTML
- **Original MCP Server**: `historical_facts_server.py` - STDIO MCP protocol for general use
- **HTTP API Wrapper**: `http_server.py` - REST API for web applications
- **Frontend Application**: Beautiful web interface with modern UI

### Performance & Reliability
- **Async HTTP Handling**: Uses `asyncio.gather()` for concurrent Wikipedia API calls
- **Error Handling**: Robust exception handling with graceful fallbacks
- **Connection Management**: Proper timeouts and connection limits
- **Response Times**: Under 10 seconds including external API calls
- **Data Volume**: Serves 20+ events per category with rich metadata

### Apps SDK Features
- **Embedded Data Templates**: Direct HTML generation bypassing ChatGPT limitations
- **Interactive Components**: Timeline, Discovery, and Map visualizations
- **Professional Styling**: Gradient backgrounds, animations, and responsive design
- **Rich Content**: 31KB+ HTML with embedded historical data

### Deployment
- **HTTPS Endpoint**: `https://enhanced-apps-sdk-morphvm-87kmb6bw.http.cloud.morph.so/mcp`
- **Live Testing**: Comprehensive visual verification completed
- **GitHub Integration**: Automated deployment and version control

## 🤝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Wikipedia and Wikimedia Foundation for providing the excellent "On This Day" API
- Anthropic for creating the Model Context Protocol
- All the historians and editors who contribute to Wikipedia's historical content

## 🐛 Issues & Support

Found a bug or need help? Please open an issue on our [GitHub repository](https://github.com/oscar-fern-labs/historical-facts-mcp-server/issues).

---

**Made with ❤️ for history enthusiasts and AI developers!**
