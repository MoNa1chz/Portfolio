# Phase 1 Mockup: Stateless vs Stateful Server Demonstration

## Overview

This is the Phase 1 mockup implementation for the stateless vs stateful server network assignment. This lightweight, runnable mockup demonstrates core concepts of stateless vs stateful server interactions through HTTP-based examples.

### Current Status
✅ **Servers Running:**
- Stateless Server: http://localhost:3000
- Stateful Server: http://localhost:3001

### Purpose
- Validate architectural concepts before committing to full Docker/Ubuntu/Nginx implementation
- Provide clear, educational examples of stateless vs stateful patterns
- Create a foundation for Phase 2 production implementation

### Key Principles
- **Simplicity**: Minimal dependencies, easy to run locally
- **Clarity**: Clear demonstration of stateless vs stateful differences
- **Educational**: Focus on concepts over production-ready code
- **Transition-ready**: Clear path to Phase 2 implementation

## What You'll Learn

By working with this mockup, you'll understand:
1. How stateless servers treat each request independently
2. How stateful servers maintain context across requests
3. The role of sessions in stateful architectures
4. Trade-offs between stateless and stateful designs
5. When to use each approach in real-world applications

## Quick Start

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager

### Installation

**On Windows (using winget):**
```powershell
# Install Node.js if not already installed
winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements

# Navigate to project directory
cd week02-stateless-stateful/phase1-mockup

# Install dependencies (use cmd if PowerShell execution policy blocks npm)
cmd /c "npm install"
```

**On Linux/macOS:**
```bash
cd week02-stateless-stateful/phase1-mockup
npm install
```

### Running the Server
```bash
# Start both stateless and stateful servers
npm start

# Or start in development mode with auto-reload
npm run dev

# Start servers individually
node start-stateless.js  # Starts on port 3000
node start-stateful.js   # Starts on port 3001
```

### Available Test Users
The following users are pre-configured for testing:
- **user001** - Test User 1 (user1@example.com) - Theme: light
- **user002** - Test User 2 (user2@example.com) - Theme: dark

### Available Test Products
- **prod001** - Sample Product A ($29.99) - Electronics
- **prod002** - Sample Product B ($19.99) - Books
- **prod003** - Sample Product C ($9.99) - Accessories

### Testing
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Quick Verification
Once the servers are running, verify they're working:

```bash
# Check stateless server
curl http://localhost:3000/health
curl http://localhost:3000/info

# Check stateful server
curl http://localhost:3001/health
curl http://localhost:3001/info

# Create a session and test stateful behavior
curl -X POST http://localhost:3001/session \
  -H "Content-Type: application/json" \
  -d '{"userId": "user001"}'
# Copy the session ID from the response and use it:
curl -H "Session-ID: YOUR_SESSION_ID" http://localhost:3001/info
```

## Server Endpoints

### Stateless Server (Port 3000)
- **GET** `/health` - Health check endpoint
- **GET** `/info` - Basic server information
- **POST** `/calculate` - Process calculations without state
- **GET** `/random` - Generate random values
- **GET** `/data` - Get mock data (stateless)
- **POST** `/data` - Process data without persistence

### Stateful Server (Port 3001)
- **GET** `/health` - Health check endpoint
- **GET** `/info` - Server information with session tracking
- **POST** `/session` - Create new session
- **GET** `/session/:id` - Retrieve session data
- **DELETE** `/session/:id` - Delete session
- **POST** `/cart/add` - Add item to shopping cart (requires session)
- **GET** `/cart` - View current cart contents (requires session)
- **DELETE** `/cart/clear` - Clear shopping cart (requires session)

## Project Structure

```
phase1-mockup/
├── README.md                          # This file
├── package.json                       # Node.js dependencies
├── server.js                          # Main server entry point
├── config/
│   └── server-config.json             # Server configuration
├── src/
│   ├── stateless-server.js            # Stateless server implementation
│   ├── stateful-server.js             # Stateful server implementation
│   ├── shared/
│   │   ├── http-helpers.js            # HTTP utility functions
│   │   ├── mock-data.js               # Mock user/data storage
│   │   └── logger.js                  # Request logging
│   └── clients/
│       ├── stateless-client.js        # Stateless client examples
│       ├── stateful-client.js         # Stateful client examples
│       └── comparison-demo.js         # Side-by-side comparison
├── examples/
│   ├── basic-requests.http            # HTTP request examples
│   ├── curl-commands.txt              # cURL examples
│   └── postman-collection.json        # Postman collection
├── tests/
│   ├── stateless.test.js              # Stateless server tests
│   ├── stateful.test.js               # Stateful server tests
│   └── integration.test.js            # Integration tests
└── docs/
    ├── concepts.md                    # Stateless vs stateful explanation
    ├── api-reference.md               # Mock API documentation
    └── transition-to-phase2.md        # Migration guide
```

## Key Concepts Demonstrated

### Stateless Server Characteristics
- No memory between requests
- Each request contains all necessary information
- Simple request/response pattern
- No session tracking
- Easily scalable horizontally
- Returns: "I have no memory of previous requests"
- Each request gets a new random value
- No user identification between requests

### Stateful Server Characteristics
- Maintains client state across requests
- Uses sessions to track user interactions
- Requires session management via Session-ID header
- Enables complex multi-step interactions (shopping carts, preferences)
- Requires sticky sessions or shared storage for scaling
- Returns: "I remember you and maintain your state across requests!"
- Tracks active sessions and shopping carts
- Remembers user context between requests

### Practical Comparison

**Scenario: Getting Server Info**

*Stateless (Port 3000):*
```bash
curl http://localhost:3000/info
# Response includes: requestCount, randomValue
# Note: "I have no memory of previous requests"
```

*Stateful (Port 3001):*
```bash
# First, create a session
curl -X POST http://localhost:3001/session -H "Content-Type: application/json" -d '{"userId":"user001"}'
# Returns: sessionId

# Then use the session
curl -H "Session-ID: <your-session-id>" http://localhost:3001/info
# Response includes: sessionInfo with userId, sessionAge, activeSessions
# Note: "I remember you and maintain your state across requests!"
```

**Key Difference:** The stateless server treats every request independently, while the stateful server remembers who you are across multiple requests using the session ID.

## Usage Examples

### Using cURL
```bash
# Stateless server - basic info
curl http://localhost:3000/info

# Stateless server - health check
curl http://localhost:3000/health

# Stateful server - create session (use user001 or user002)
curl -X POST http://localhost:3001/session \
  -H "Content-Type: application/json" \
  -d '{"userId": "user001"}'

# Stateful server - get info with session
curl -H "Session-ID: YOUR_SESSION_ID_HERE" http://localhost:3001/info

# Add item to cart (requires session)
curl -X POST http://localhost:3001/cart/add \
  -H "Content-Type: application/json" \
  -H "Session-ID: YOUR_SESSION_ID_HERE" \
  -d '{"productId": "prod001", "quantity": 2}'
```

### Using the Example Clients
```bash
# Run stateless client example
node src/clients/stateless-client.js

# Run stateful client example  
node src/clients/stateful-client.js

# Run comparison demo
node src/clients/comparison-demo.js
```

**Note:** If you get "Cannot find module 'axios'" error, install it:
```bash
npm install axios
# Or on Windows with PowerShell:
& "C:\Program Files\nodejs\npm.cmd" install axios
```

**What Each Demo Shows:**

1. **stateless-client.js** - Demonstrates:
   - Each request is independent
   - Different random values each time
   - Calculations without context storage
   - No session management needed

2. **stateful-client.js** - Demonstrates:
   - Session creation and management
   - Shopping cart functionality
   - User preferences persistence
   - Context maintained across requests

3. **comparison-demo.js** - Shows side-by-side:
   - Same operations on both servers
   - Clear architectural differences
   - When to use each approach

### Windows PowerShell Examples
If using PowerShell on Windows, use these commands:

```powershell
# Create a session
$body = @{userId='user001'} | ConvertTo-Json
curl -UseBasicParsing -Method POST -Uri http://localhost:3001/session `
  -ContentType 'application/json' -Body $body | Select-Object -ExpandProperty Content

# Use the session (replace YOUR_SESSION_ID with actual ID from above)
curl -UseBasicParsing -Headers @{'Session-ID'='YOUR_SESSION_ID'} `
  http://localhost:3001/info | Select-Object -ExpandProperty Content

# Add item to cart
$cartBody = @{productId='prod001'; quantity=2} | ConvertTo-Json
curl -UseBasicParsing -Method POST -Uri http://localhost:3001/cart/add `
  -Headers @{'Session-ID'='YOUR_SESSION_ID'; 'Content-Type'='application/json'} `
  -Body $cartBody | Select-Object -ExpandProperty Content
```

## Testing Strategy

### Unit Tests
- Test individual server components
- Verify stateless behavior (no persistence)
- Verify stateful behavior (session persistence)

### Integration Tests
- Test client-server interactions
- Verify API contract compliance
- Test error handling and edge cases

### Validation Tests
- Ensure concepts are clearly demonstrated
- Verify educational examples work as expected

## Transition to Phase 2

This mockup is designed to transition smoothly to Phase 2 (Production Implementation):

1. **API Compatibility**: Phase 2 will maintain similar API endpoints
2. **Data Models**: Mock data structures map to PostgreSQL schema
3. **Session Management**: In-memory sessions map to Redis storage
4. **Configuration**: Environment-based configuration for production

See `docs/transition-to-phase2.md` for detailed migration guide.

## Troubleshooting

### Port Already in Use
If you see "EADDRINUSE" error:
```bash
# On Windows
netstat -ano | findstr :3000
netstat -ano | findstr :3001

# Kill the process using the port
taskkill /PID <process_id> /F
```

### PowerShell Execution Policy (Windows)
If npm commands fail in PowerShell:
```powershell
# Use cmd instead
cmd /c "npm install"
cmd /c "node start-stateless.js"

# Or bypass execution policy for current session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Session Expired
Sessions expire after 15 minutes. If you get "Session not found":
- Create a new session using POST /session
- Use the new session ID in subsequent requests

### Invalid User ID
Make sure to use valid test users:
- user001
- user002

Do not use arbitrary user IDs like "user123" - they won't work.

### Missing axios Module
If client demos fail with "Cannot find module 'axios'":
```powershell
# Install axios
npm install axios

# Or use full path on Windows
& "C:\Program Files\nodejs\npm.cmd" install axios
```

### Node.js Not Found in PowerShell
If node commands don't work after installation:
```powershell
# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Or use full path
& "C:\Program Files\nodejs\node.exe" start-stateless.js
```

## Demo Results Summary

After running the demo clients successfully, you'll see:

### Stateless Demo Highlights
- ✅ Each `/info` request returns different random values
- ✅ Calculations complete without server memory
- ✅ No session tracking - client ID is just a label
- ✅ Request count increments (server-wide, not per-client)

### Stateful Demo Highlights
- ✅ Session created with 15-minute expiry
- ✅ Shopping cart persists across requests
- ✅ User preferences maintained
- ✅ Server tracks active sessions and carts

### Comparison Demo Highlights
- ✅ Side-by-side execution on both servers
- ✅ Clear visualization of architectural differences
- ✅ Same operations, different behaviors
- ✅ Demonstrates when to use each approach

## License

Educational use - part of network assignment project.

## Contributing

This is an educational project. Feedback and improvements are welcome through the main project repository.

---

## Learning Outcomes

After completing this phase, you should understand:

### ✅ Stateless Architecture
- No memory between requests
- Each request is self-contained
- Easy horizontal scaling
- Simple request/response pattern
- Perfect for: REST APIs, microservices, CDNs

### ✅ Stateful Architecture  
- Maintains client state via sessions
- Enables complex workflows (shopping carts)
- Requires session management
- Scaling needs sticky sessions or shared storage
- Perfect for: E-commerce, dashboards, user apps

### ✅ Practical Trade-offs
- **Stateless**: Scalable but verbose (must send all context)
- **Stateful**: Rich features but complex scaling
- **Session Layer**: Application's responsibility, not TCP's
- **Real-world**: Often use both (stateless API + stateful UI)

### 🎯 Key Insight
> "TCP keeps connections alive. Applications decide whether conversations remember anything. The Session Layer is where software chooses: Am I talking once, or are we building a relationship?"

**Next Steps:** Proceed to Phase 2 for production-grade implementation with Redis, PostgreSQL, and Docker containerization.