from tools import Tool


class WebSearch(Tool):
    name = "web_search"
    description = "Search the web (DuckDuckGo) for recent public information. Returns top results."
    args_doc = '{"query": "home care for fever adults", "max_results": 3}'

    def execute(self, query, max_results=3):
        try:
            from duckduckgo_search import DDGS
            hits = list(DDGS().text(query, max_results=int(max_results)))
        except Exception as e:
            return f"ERROR: web search unavailable ({type(e).__name__}). Continue with local data."
        if not hits:
            return "No results."
        return "\n".join(f"- {h.get('title')}: {h.get('body')} ({h.get('href')})" for h in hits)
