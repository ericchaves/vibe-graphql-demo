import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from schema import schema

# Create the GraphQL router
graphql_router = GraphQLRouter(schema)

# Create the FastAPI application
app = FastAPI()

# Include the GraphQL router
app.include_router(graphql_router, prefix="/graphql")

@app.get("/")
async def read_root():
    return {"message": "GraphQL Filter Demo API is running. Go to /graphql for the GraphQL playground."}

# To run this application, you would typically use a command like:
# uvicorn main:app --reload
# inside the devcontainer.
