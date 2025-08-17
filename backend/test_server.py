from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Test Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test server is running"}

@app.get("/api/test")
async def test_endpoint():
    return {"status": "ok", "message": "API is working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)