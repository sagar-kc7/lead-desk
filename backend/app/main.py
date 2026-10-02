from fastapi import FastAPI

app = FastAPI(title="Lead Desk API")


@app.get("/api/health")
def health():
    return {"status": "ok"}
