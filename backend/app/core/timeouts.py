# Live search may wait this long between the provider call and the orchestrator
# cap. SerpAPI cold queries have been measured at 7-20 s, and showing a long
# spinner beats swapping in unrelated catalog products during a demo.
SEARCH_S = 11.0
# One immersive lookup per listing runs concurrently; a slow one must not hold
# the grid. Anything slower keeps its Google Shopping link, which still works.
IMMERSIVE_STORE_S = 3.5
INVESTIGATION_BUDGET_S = 14.0
CHECK_CONCURRENCY = 8
LLM_S = 2.5
DOMAIN_AGE_S = 4.0
SSL_S = 4.0
SAFE_BROWSING_S = 3.0
REDDIT_S = 4.0
PAGE_FLAGS_S = 6.0
MAX_LISTINGS = 9  # the demo catalog has 8 safe listings plus the villain
