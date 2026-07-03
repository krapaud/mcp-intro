"""Agent-like client for the Programming Learning MCP server.

This program receives a student question, connects to the MCP server as an
external capability (never importing server functions directly), calls
search_topics and get_topic_details through MCP, and formats a short
student-facing answer from the returned data.

Run with: python3 client/agent.py "I want to study Python decorators. What should I review first?"
"""

import asyncio
import re
import sys
from pathlib import Path

from fastmcp import Client

SERVER_PATH = Path(__file__).resolve().parent.parent / "server" / "learning_server.py"

STOPWORDS = {
    "i", "want", "to", "study", "what", "should", "review", "first",
    "the", "a", "an", "about", "learn", "is", "are", "how", "do", "does",
    "explain", "me", "for", "on", "in", "of", "and",
}


def extract_query(question: str) -> str:
    words = re.findall(r"[a-zA-Z-]+", question.lower())
    keywords = [w for w in words if w not in STOPWORDS]
    return " ".join(keywords) if keywords else question


def format_response(question: str, matches: list[dict], details: dict | None) -> str:
    lines = [f"# Study Assistant Response\n", f"**Question:** {question}\n"]

    if not matches or details is None or "error" in details:
        lines.append("No matching topic was found in the MCP server's dataset for this question.")
        return "\n".join(lines)

    lines.append(f"## Recommended topic: {details['title']}\n")
    lines.append(f"**Why it's relevant:** {details['summary']}\n")

    lines.append("**Prerequisites:**")
    for p in details["prerequisites"]:
        lines.append(f"- {p}")
    lines.append("")

    lines.append("**Key concepts:**")
    for k in details["key_concepts"]:
        lines.append(f"- {k}")
    lines.append("")

    lines.append("**Common mistakes to avoid:**")
    for m in details["common_mistakes"]:
        lines.append(f"- {m}")
    lines.append("")

    lines.append(f"**Practice idea:** {details['practice_idea']}")

    return "\n".join(lines)


async def run_agent(question: str) -> str:
    client = Client(str(SERVER_PATH))
    async with client:
        query = extract_query(question)
        search_result = await client.call_tool("search_topics", {"query": query})
        matches = search_result.data

        details = None
        if matches:
            top_match = matches[0]
            details_result = await client.call_tool(
                "get_topic_details", {"topic_id": top_match["id"]}
            )
            details = details_result.data

        return format_response(question, matches, details)


def main() -> None:
    question = " ".join(sys.argv[1:]) or "I want to study Python decorators. What should I review first?"
    response = asyncio.run(run_agent(question))
    print(response)


if __name__ == "__main__":
    main()
