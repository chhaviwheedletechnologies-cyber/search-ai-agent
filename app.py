from fastapi import FastAPI

from routes.search_routes import router

app=FastAPI(title="Search AI Agent")

app.include_router(router)

@app.get("/")

def home():

    return{"message":"Search AI Agent Running"}