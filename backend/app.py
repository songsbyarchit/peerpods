from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database import engine
from backend.routes import pods, users, messages, auth_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")

# Allow frontend to talk to backend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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