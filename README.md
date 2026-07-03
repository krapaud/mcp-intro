# MCP Servers in Python

## Description

This project is a **Programming Learning MCP Server**: a small [FastMCP](https://gofastmcp.com) server that exposes a local dataset of programming topics (decorators, generators, exceptions, etc.) through the Model Context Protocol. A simple agent-like client connects to the server, searches for a topic based on a student's question, retrieves its full details, and formats a short study-friendly answer — all without ever importing the server's Python functions directly.

## MCP Architecture Summary

**MCP (Model Context Protocol)** is a standard protocol that lets AI applications connect to external capabilities (data, tools, prompts) in a uniform way, instead of every application writing a custom integration for every API or data source.

- **MCP Host**: the AI application the user actually interacts with (e.g. an agent, a chat app, an IDE assistant). It manages the overall conversation and decides when it needs external help.
- **MCP Client**: the component, created by the host, that maintains a 1:1 connection to a single MCP server. A host that needs three different capabilities from three servers creates three clients.
- **MCP Server**: a program that exposes capabilities — tools, resources, and/or prompts — over the protocol. It doesn't know or care what host is using it; it just answers requests. In this project, `server/learning_server.py` is the MCP server.

**Tools vs. resources**:
- A **tool** is an action or computation the client can invoke with arguments (like calling a function): `search_topics(query)` and `get_topic_details(topic_id)` in this project.
- A **resource** is read-only data identified by a URI that the client can fetch, with no side effects and no arguments to reason about: `topics://catalog` in this project.

**Why expose only what's needed**: every tool and resource a server exposes is something a connected agent can call, potentially based on an LLM's own judgment. A server that exposes broad or unnecessary capabilities (e.g. arbitrary file writes, unrestricted shell access) increases the blast radius if the agent misuses a tool or is manipulated by malicious input. Keeping the surface small — here, just search/details/catalog over a local read-only JSON file — makes the server easy to reason about and safe to connect to an autonomous agent.

Example flow: an agent receives "I want to study Python decorators", calls `search_topics("decorators")` on the MCP server, gets back a topic id, calls `get_topic_details("python-decorators")`, and uses the returned prerequisites/key concepts/practice idea to write its answer.

## Requirements

- Python 3.10+
- `fastmcp` (see `requirements.txt`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # not required unless you add LLM/HTTP config
```

## How to Run the Server

The server runs over stdio by default and is normally started automatically by a client/agent (as in `client/mcp_client.py` and `client/agent.py`, which launch it as a subprocess via `fastmcp.Client`).

To confirm it starts cleanly on its own:

```bash
python3 server/learning_server.py
```

It will print the FastMCP startup banner and wait on stdio (Ctrl+C to stop).

## How to Test the Server

A test script (`client/mcp_client.py`) connects to the server, lists tools/resources, and calls each capability with both valid and invalid input:

```bash
python3 client/mcp_client.py
```

Sample output observed:

```
Available tools: ['search_topics', 'get_topic_details']
Available resources: ['topics://catalog']

--- search_topics('decorators') ---
[{'id': 'python-decorators', 'title': 'Python Decorators', 'summary': '...'}]

--- search_topics('nonexistent-topic-xyz') ---
[]

--- get_topic_details('python-decorators') ---
{'id': 'python-decorators', ... 'practice_idea': '...'}

--- get_topic_details('does-not-exist') ---
{'error': "No topic found with id 'does-not-exist'"}

--- resource topics://catalog ---
[{"id": "python-decorators", "title": "Python Decorators"}, ...]
```

This confirms: the server starts, tools are listed, both tools return correct data for valid input, both handle invalid/no-match input without crashing, and the resource is readable.

You can alternatively use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) by pointing it at `python3 server/learning_server.py`.

## How to Run the Agent

`client/agent.py` is a deterministic agent-like client: it does not import the server's Python functions, it connects to the server exclusively through `fastmcp.Client` (an MCP client), calls `search_topics` then `get_topic_details`, and formats the response.

```bash
python3 client/agent.py "I want to study Python decorators. What should I review first?"
```

A saved sample run is in [output/sample_agent_response.md](output/sample_agent_response.md).

## Available Tools

| Tool | Input | Output | Notes |
|---|---|---|---|
| `search_topics` | `query: str` | `list[dict]` of `{id, title, summary}` | Case-insensitive match against title and key concepts. Returns `[]` if nothing matches. |
| `get_topic_details` | `topic_id: str` | `dict` with full topic fields, or `{"error": ...}` | Exact id lookup. Never raises on an unknown id. |

## Available Resources

| Resource URI | Returns | Notes |
|---|---|---|
| `topics://catalog` | JSON string: list of `{id, title}` for every topic | Read-only, no arguments, backed by `data/topics.json`. |

## Third-Party MCP Server Review

**Server reviewed:** the official [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) (`@modelcontextprotocol/server-filesystem`), maintained under the `modelcontextprotocol/servers` reference repository.

- **What it does**: exposes tools to read, write, list, search, and move files/directories on the local filesystem, so an LLM-based agent can operate on a project directory.
- **Local or remote**: local — it runs as a subprocess on the user's own machine, launched via stdio (typically through `npx`), not a hosted remote service.
- **Tools/resources exposed**: tools such as `read_file`, `write_file`, `list_directory`, `create_directory`, `move_file`, `search_files`, and `get_file_info`; directories are exposed as resources for browsing.
- **Permissions/credentials required**: no API keys, but it requires explicit filesystem access — the directories it's allowed to touch are passed as startup arguments/config, and it can read and overwrite any file under those directories.
- **One risk**: if configured with too broad a root directory (e.g. the user's home folder instead of one project folder), a manipulated or overly autonomous agent could read sensitive files (SSH keys, `.env` files, credentials) or overwrite important data outside the intended scope.
- **One safety measure**: restrict the allowed root(s) to the single project directory actually needed for the task, and review the exact directory list in the client's MCP configuration file before first use rather than accepting a default like the home directory.

## Example Output

See [output/sample_agent_response.md](output/sample_agent_response.md) for a full saved run of `client/agent.py` against the question *"I want to study Python decorators. What should I review first?"*.

## Known Limitations

- `search_topics` uses simple case-insensitive substring matching, not semantic search — a query like "logging function calls" will not match "decorators" unless the words overlap.
- The agent's keyword extraction (`client/agent.py`) is a basic stopword filter, not an LLM; it can pick a suboptimal query for oddly phrased questions.
- The dataset (`data/topics.json`) only contains six topics; unrelated questions will correctly report "no matching topic" rather than inventing one.
- The server keeps no state between calls (topics are re-read from disk each call), which is simple but not optimized for very large datasets.

## Reflection

**What problem does MCP solve?** It standardizes how AI applications connect to external tools and data, so a single server implementation (like this one) can be reused by any MCP-compatible client or agent framework, instead of writing a bespoke integration per application.

**Difference between an MCP tool and an MCP resource?** A tool is an invokable action with input parameters and possible side effects (here: searching or looking up a topic). A resource is read-only data fetched by URI with no parameters (here: the topic catalog).

**What does this MCP server expose?** Two tools (`search_topics`, `get_topic_details`) and one resource (`topics://catalog`) over a local JSON dataset of six programming topics.

**How does the agent use the MCP server?** `client/agent.py` connects with `fastmcp.Client`, calls `search_topics` with keywords extracted from the student's question, takes the first match, calls `get_topic_details` with that topic's id, and formats the returned fields (prerequisites, key concepts, mistakes, practice idea) into a markdown answer. It never imports server code directly.

**What should you check before using a third-party MCP server?** What it actually does, whether it runs locally or remotely, exactly which tools/resources it exposes, what credentials or filesystem/network access it requires, and whether its permission scope can be restricted to only what the task needs.

**What limitation did I observe?** The biggest one is that keyword-based search is brittle — it works well for the direct test prompt but would miss topics phrased very differently from their titles/key concepts. A production version would likely need fuzzy or embedding-based search.
