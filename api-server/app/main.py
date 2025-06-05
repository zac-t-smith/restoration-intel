from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, projects, finance
from .jobs.kpi_scheduler import start_scheduler

app = FastAPI(title="Restoration Intel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
async def root():
    return {"message": "Restoration Intel API"} 