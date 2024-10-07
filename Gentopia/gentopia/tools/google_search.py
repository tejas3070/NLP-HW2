from typing import AnyStr, Optional, Type, Any
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from gentopia.tools.basetool import BaseTool
import os

class GoogleSearchArgs(BaseModel):
    query: str = Field(..., description="A search query")

class GoogleSearch(BaseTool):
    """Tool that adds the capability to query the Google Custom Search API."""
    name = "google_search"
    description = ("A search engine retrieving top search results using Google's Custom Search API."
                   "Input should be a search query.")
    args_schema: Optional[Type[BaseModel]] = GoogleSearchArgs

    def google_search(self, query: AnyStr, num_results: int = 10) -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
        return '\n\n'.join([item['title'] + "\n" + item['link'] for item in res.get('items', [])])

    def _run(self, query: AnyStr) -> str:
        return self.google_search(query)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "__main__":
    google_search_tool = GoogleSearch()
    ans = google_search_tool._run("Attention for transformer")
    print(ans)
