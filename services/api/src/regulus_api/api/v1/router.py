from fastapi import APIRouter

from regulus_api.api.v1 import graph, repos

api_router = APIRouter()
api_router.include_router(repos.router, prefix="/repos", tags=["repos"])
api_router.include_router(graph.router, tags=["graph"])
