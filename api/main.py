from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="Subscription API",
    description="API for subscription management",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Subscription API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# AWS Lambda handler
handler = Mangum(app)
