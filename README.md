# MCP for Dalux

## Introduction
This project is a graduation project developed as a prototype. It provides an integration layer between Dalux (via its REST API) and an LLM (via MCP through FastMCP), with an optional parallel MCP-inspired track for direct integration to an LLM via API. The goal of the project is to make Dalux data available via natural prompting to improve insight into project data.

Its central use case is: An employee needs insight into project data and sends a natural-language query to the system. The system processes the request using available project data and returns an answer the employee uses to gain professional insight and support further work.

Primary data source: Dalux REST API (Build API v4.12)
- https://app.swaggerhub.com/apis/Dalux/DaluxBuild-api/4.12#/

## Two Access Tracks (MCP and HTTP)
The system exposes two access tracks by design. The MCP track is used to expose tools through the MCP protocol (useful for development, testing, and direct MCP clients). The HTTP track is MCP-inspired and routes requests through the system's own API for more flexible integration patterns. Both tracks share the same tool and Dalux integration layers to avoid duplicated logic, keep responsibilities clear, and support flexibility in how clients integrate with the system. Either track can be removed and the other will still work. See the diagrams folder for an overview of the separate tracks.

## Repository Branches
- MVP1: First MVP MCP server.
- MVP2: Expands MVP1 logic and adds the HTTP track.
- deploy/azure-mcp: Automatic Azure deployment via relevant YAML workflows.
- feat/stdio-to-http-orchestration: Transition work between MVP1 and MVP2.

## Diagrams Provided
The project provides UML-inspired diagrams for an overview of the system and key design choices. These are available in /diagrams (partly in Danish):
- Object- and Domain Model
- System Sequence Diagram and Operations Contracts
- Component- and Layer Diagram
- Design Class Diagram
- Sequence Diagram

## How to Use
### Configuration overview
Configuration is centralized in the app config and environment variables. At a high level you will:
- create an .env file with Dalux credentials and service settings
- adjust configuration defaults in code when needed
- start either the MCP server or the HTTP API

### Basic setup
1) Create an .env file with Dalux credentials and service settings.
2) Populate required credentials for the Dalux and LLM API (if using the HTTP-track).
3) Start the application using your preferred entry point (MCP or HTTP API) by adjusting config.
4) If using MCP, choose a transport protocol (stdio or streamable-http) and a compatible MCP-client.
5) If using HTTP, choose a supported LLM (any implementation of BaseClient) and send your API REST requests to the system's endpoints (routes_sessions.py). Make sure you have a valid API key for the model's API set in the .env.

## Current State
- MCP integration and a standalone HTTP API are both functional.
- Supports logging of LLM-actions, API-requests and other debugging (/logs)
- Only uses light smoke testing for external dependencies. (/tests)
- Focused on core data access and tool execution to enable experimentation and insights.
- Not yet enterprise-ready: no user administration, database, heavy security or advanced operational features.

## Suggestions and Challenges
Suggested improvements:
- Expand to other data on the Dalux API (e.g. Files) or entirely new data sources
- Adjust the instructions for the AI as needed in /instructions or the tool definitions in tool_registry.py
For production:
- Implement user administration, auth and role-based access control.
- Add persistent storage for sessions and messages in the HTTP-track.
- Strengthen prompt pre-processing and sanitization in InputPolicy.
- Focus the integration on either access track and a specific LLM.
Key challenges:
- Handling large amounts of relatively unorganized data on the Dalux API.
- Polishing the LLM's memory of messages in the HTTP-track. (where SDKs don't natively support memory)
- Ensuring robust testing, error handling and insights across long tool chains.

The project is considered complete as of June, 2026.