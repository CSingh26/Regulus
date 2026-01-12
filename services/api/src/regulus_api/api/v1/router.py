from fastapi import APIRouter

from regulus_api.api.v1 import diff, graph, metrics, rag, repos

api_router = APIRouter()
api_router.include_router(repos.router, prefix="/repos", tags=["repos"])
api_router.include_router(graph.router, tags=["graph"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(diff.router, tags=["diff"])
api_router.include_router(metrics.router, tags=["metrics"])
