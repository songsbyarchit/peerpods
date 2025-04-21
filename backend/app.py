from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database import engine
from backend.routes import pods, users, messages, auth_routes

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router, prefix="/auth")

# Allow frontend to talk to backend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(pods.router, prefix="/pods", tags=["Pods"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

@app.get("/")
def read_root():
    return {"message": "PeerPods backend running"}