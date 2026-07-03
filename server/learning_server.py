import json
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Programming Learning Server")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "topics.json"


def _load_topics() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or key concept keyword."""
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    topics = _load_topics()
    matches = []
    for topic in topics:
        title_match = query_lower in topic["title"].lower()
        concept_match = any(query_lower in concept.lower() for concept in topic["key_concepts"])
        if title_match or concept_match:
            matches.append(
                {
                    "id": topic["id"],
                    "title": topic["title"],
                    "summary": topic["summary"],
                }
            )
    return matches


@mcp.tool
def get_topic_details(topic_id: str) -> dict:
    """Return full information for a topic by id, or an error message if not found."""
    topics = _load_topics()
    for topic in topics:
        if topic["id"] == topic_id:
            return topic
    return {"error": f"No topic found with id '{topic_id}'"}


@mcp.resource("topics://catalog")
def get_topic_catalog() -> str:
    """Return the list of available topic ids and titles as a JSON string."""
    topics = _load_topics()
    catalog = [{"id": t["id"], "title": t["title"]} for t in topics]
    return json.dumps(catalog)


if __name__ == "__main__":
    mcp.run()
