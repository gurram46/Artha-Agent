# Fi Money MCP Setup Reference

## 1. For AI Assistants (Claude Desktop/Cursor/Windsurf)

Add this to your AI assistant's MCP configuration:

```json
{
  "mcpServers": {
    "fi_mcp": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.fi.money:8080/mcp/stream"]
    }
  }
}
```

### Where to add this:
- **Claude Desktop**: Settings > Developer > Add/Edit Config
- **Cursor/Windsurf**: Settings > Tools & Integrations > Add Custom MCP

## 2. For Artha AI Backend

Update the `.env` file in the backend folder:

```env
FI_MCP_AUTH_TOKEN=your_actual_token_here
```

Replace `your_actual_token_here` with your real Fi Money MCP authentication token.

## How to Get Your Token

1. Visit: https://fi.money/features/getting-started-with-fi-mcp
2. Follow Fi Money's authentication process
3. Get your MCP authentication token
4. Replace the placeholder in both configurations

## Current Status

- ✅ AI Assistant MCP Config: Ready to use
- ❌ Artha AI Backend Token: Needs real token
- ✅ Backend Server: Running on port 8000
- ✅ Frontend App: Running on port 3000

## Testing

Once you have the real token:
1. Update the `.env` file
2. Restart the backend server
3. Test Fi Money authentication in the Artha AI app