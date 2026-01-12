from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from regulus_api.db.models import GraphEdge, GraphNode, Repo
from regulus_api.db.session import get_session
from regulus_api.jobs.queue import get_queue
from regulus_api.jobs.tasks import build_graph

router = APIRouter()


class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str


class GraphNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    kind: str
    loc: int
    in_degree: int
    out_degree: int


class GraphEdgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_node_id: int
    to_node_id: int
    kind: str
    weight: int


class GraphResponse(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]


@router.post(
    "/repos/{repo_id}/graph",
    response_model=JobEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_graph_build(
    repo_id: int, session: Session = Depends(get_session)
) -> JobEnqueueResponse:
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    queue = get_queue()
    job = queue.enqueue(build_graph, repo_id)
    return JobEnqueueResponse(job_id=job.id, status="queued")


@router.get("/graph/{repo_id}", response_model=GraphResponse)
def get_graph(repo_id: int, session: Session = Depends(get_session)) -> GraphResponse:
    nodes = session.exec(select(GraphNode).where(GraphNode.repo_id == repo_id)).all()
    edges = session.exec(select(GraphEdge).where(GraphEdge.repo_id == repo_id)).all()

    in_degree: dict[int, int] = defaultdict(int)
    out_degree: dict[int, int] = defaultdict(int)
    for edge in edges:
        out_degree[edge.from_node_id] += 1
        in_degree[edge.to_node_id] += 1

    node_out: list[GraphNodeOut] = []
    for node in nodes:
        if node.id is None:
            continue
        node_out.append(
            GraphNodeOut(
                id=node.id,
                name=node.name,
                path=node.path,
                kind=node.kind,
                loc=node.loc,
                in_degree=in_degree.get(node.id, 0),
                out_degree=out_degree.get(node.id, 0),
            )
        )

    edge_out: list[GraphEdgeOut] = []
    for edge in edges:
        if edge.id is None:
            continue
        edge_out.append(
            GraphEdgeOut(
                id=edge.id,
                from_node_id=edge.from_node_id,
                to_node_id=edge.to_node_id,
                kind=edge.kind,
                weight=edge.weight,
            )
        )

    return GraphResponse(nodes=node_out, edges=edge_out)
