from fastapi import FastAPI
from api.routes import crawl, jobs, results
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for RPA Challenge - Web Scraping & Queue Processing",
    version="0.1.0",
)

app.include_router(crawl.router, prefix="/crawl", tags=["crawling"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(results.router, prefix="/results", tags=["results"])

@app.get("/")
def read_root():
    return {"message": "Welcome to RPA Challenge API", "docs_url": "/docs"}
