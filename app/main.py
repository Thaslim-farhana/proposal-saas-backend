from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
import os

app = FastAPI(title="Lovable SaaS API")

# CORS: allow your frontend URL(s)
origins = [
    "https://yourapp.vercel.app",     # production (Vercel)
    "https://yourapp.lovable.dev",    # optional (lovable staging)
    "http://localhost:5173",          # dev (Vite)
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")

@app.get("/api/")
async def root():
    return {"message": "Lovable SaaS API is running"}
