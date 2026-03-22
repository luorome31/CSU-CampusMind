# Playwright MCP Usage

This project includes Playwright MCP server for frontend development.

## Purpose

Use Playwright MCP when you need to:

- **Verify UI behavior** - Take snapshots, check element visibility
- **Debug layout issues** - Inspect rendered DOM and CSS
- **Test user flows** - Click, type, navigate through pages
- **Observe runtime state** - Evaluate JavaScript in browser context

## Available MCP Tools

- `browser_navigate` - Navigate to a URL
- `browser_snapshot` - Capture accessibility snapshot of current page
- `browser_take_screenshot` - Take screenshot
- `browser_click` - Click an element
- `browser_type` - Type text into element
- `browser_evaluate` - Run JavaScript in page context
- `browser_network_requests` - View network requests
- `browser_console_messages` - View console output

## Common Usage Patterns

### Start Frontend Dev Server First

```bash
tmux new-session -d -s campusmind-frontend 'cd /home/luorome/software/CampusMind/frontend && npm run dev'
```

### Verify Page Renders Correctly

```javascript
// Navigate to the page
await browser_navigate({ url: "http://localhost:5173" })

// Take snapshot to see current state
await browser_snapshot({})

// Take screenshot for visual verification
await browser_take_screenshot({ type: "png" })
```

### Debug Layout Issues

```javascript
// Get accessibility snapshot
await browser_snapshot({})

// Evaluate custom JavaScript
await browser_evaluate({
  function: "() => getComputedStyle(document.body).backgroundColor"
})
```

### Check Console Errors

```javascript
await browser_console_messages({ level: "error" })
```

## Notes

- MCP server must be enabled in Claude Code settings
- Ensure dev server is running before using browser tools
- Use `localhost:5173` for frontend dev server
