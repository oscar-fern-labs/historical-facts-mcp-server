# Historical Facts Explorer Frontend

A beautiful, responsive web application that provides an intuitive interface for exploring historical facts using the Historical Facts MCP Server API.

## 🌟 Features

### Core Functionality
- **Today in History**: Discover what happened on the current date
- **Random Discovery**: Get surprised with random historical facts
- **Date Explorer**: Search for facts on any specific date
- **Smart Filtering**: Filter by events, births, deaths, and holidays

### User Experience
- **Modern Design**: Clean, professional interface with smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Visual Content**: Thumbnails and images from Wikipedia
- **Interactive Elements**: Hover effects, smooth scrolling, and transitions
- **Real-time Status**: API connectivity indicator

### Technical Features
- **Pure Frontend**: No build process required - HTML, CSS, and JavaScript
- **Fast Loading**: Optimized assets and efficient code
- **Error Handling**: Graceful error messages and retry mechanisms
- **Keyboard Support**: Full keyboard navigation support
- **Cross-browser Compatible**: Works in all modern browsers

## 🚀 Live Demo

**Frontend URL**: https://frontend-morphvm-87kmb6bw.http.cloud.morph.so
**API Backend**: https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so

## 📁 Files

- `index.html` - Main application with enhanced UI and full CSS styling
- `script-enhanced.js` - Enhanced JavaScript with full functionality
- `test.html` - Simple test version used for development
- `script.js` - Basic JavaScript functionality  
- `styles.css` - Additional custom styles (legacy)
- `server.py` - Python HTTP server for local development
- `README.md` - This documentation

## 🏃‍♂️ Quick Start

### Option 1: Direct Access
Visit the live application at: https://frontend-morphvm-87kmb6bw.http.cloud.morph.so

### Option 2: Local Development
```bash
# Navigate to frontend directory
cd frontend

# Start local server
python3 -m http.server 3000

# Open browser to http://localhost:3000
```

### Option 3: Custom Server
```bash
# Use the custom Python server
python3 server.py 3000
```

## 🎨 User Interface

### Main Features
1. **Header**: Branding and API status indicator
2. **Hero Section**: Welcome message and call-to-action
3. **Action Cards**: Three main interaction options
4. **Filter Tabs**: Category filtering (appears after search)
5. **Results Area**: Dynamic content display
6. **Footer**: Links to documentation and repository

### Design Principles
- **Accessibility**: Semantic HTML and keyboard navigation
- **Performance**: Lazy loading and optimized requests  
- **Usability**: Intuitive interface with clear visual hierarchy
- **Aesthetics**: Modern design with consistent spacing and typography

## 🔌 API Integration

The frontend connects to the Historical Facts MCP Server API:

### Endpoints Used
- `GET /health` - API health check
- `GET /historical-facts/today` - Today's historical facts
- `GET /historical-facts/random` - Random historical fact
- `GET /historical-facts/{month}/{day}` - Facts for specific date

### Data Processing
- **Filtering**: Client-side filtering by event type
- **Formatting**: Date formatting and text truncation
- **Images**: Wikipedia thumbnail integration with fallbacks
- **Links**: Direct links to Wikipedia articles

## 🛠️ Technical Stack

- **HTML5**: Semantic markup and accessibility features
- **CSS3**: Modern styling with flexbox/grid and animations
- **JavaScript ES6+**: Async/await, modules, and modern syntax
- **Google Fonts**: Inter font family for clean typography
- **Wikipedia API**: Rich content and imagery integration

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px - Single column layout
- **Tablet**: 768px - 1024px - Adapted grid layout  
- **Desktop**: > 1024px - Full multi-column layout

### Adaptive Features
- **Navigation**: Collapsible elements on small screens
- **Typography**: Scalable text sizes
- **Images**: Responsive thumbnails and fallbacks
- **Touch**: Touch-friendly interaction areas

## 🎯 Usage Examples

### Exploring Today's History
1. Click "Today in History" card
2. Browse through different categories using filter tabs
3. Click Wikipedia links to learn more

### Random Discovery
1. Click "Random Discovery" for a surprise fact
2. Each click generates a new random historical event
3. Facts come from various dates throughout history

### Date Search
1. Select month and day from dropdowns
2. Click "Explore Date" to see results
3. Use filters to focus on specific types of events

## 🔧 Development

### Local Setup
```bash
# Clone repository
git clone https://github.com/oscar-fern-labs/historical-facts-mcp-server.git
cd historical-facts-mcp-server/frontend

# Start development server
python3 -m http.server 3000
```

### File Structure
```
frontend/
├── index.html              # Main application
├── script-enhanced.js       # Core JavaScript
├── test.html               # Development test page
├── script.js               # Basic functionality
├── styles.css              # Legacy styles
├── server.py               # Development server
└── README.md               # Documentation
```

### Customization
- **Colors**: Edit CSS custom properties in `index.html`
- **Layout**: Modify CSS Grid and Flexbox properties
- **Functionality**: Update JavaScript in `script-enhanced.js`
- **Content**: Customize text and messaging

## 🌍 Browser Support

- **Chrome**: 70+ ✅
- **Firefox**: 65+ ✅  
- **Safari**: 12+ ✅
- **Edge**: 79+ ✅

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please see the main repository for contribution guidelines.

## 📞 Support

For issues or questions:
- **GitHub Issues**: https://github.com/oscar-fern-labs/historical-facts-mcp-server/issues
- **API Documentation**: https://historical-facts-api-morphvm-87kmb6bw.http.cloud.morph.so/docs
