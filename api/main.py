from fastapi import FastAPI
from mangum import Mangum

from routers import user_router, plan_router, subscription_router, report_router

app = FastAPI(
    title="Shade Subscription API",
    description="API for subscription management",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(plan_router)
app.include_router(subscription_router)
app.include_router(report_router)


@app.get("/")
def root():
    return {"message": "Shade Subscription API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# AWS Lambda handler
handler = Mangum(app)
