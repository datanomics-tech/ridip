from fastapi import FastAPI

app = FastAPI(
    title="RIDIP API",
    description="Rwanda Integrated Data Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    """Simple check that the API is running."""
    return {"status": "ok", "service": "ridip-api"}