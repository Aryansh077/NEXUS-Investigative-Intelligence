from fastapi import APIRouter, HTTPException
from ..services.graph.analytics import graph_for_case, find_path, graph_metrics

router = APIRouter()

@router.get("/{case_id}")
def get_graph(case_id: str, entity_type: str | None = None, search: str | None = None):
    return graph_for_case(case_id, entity_type=entity_type, search=search)

@router.get("/{case_id}/path")
def path(case_id: str, source: str, target: str):
    result = find_path(case_id, source, target)
    if result is None:
        raise HTTPException(404, "No path found")
    return result

@router.get("/{case_id}/metrics")
def metrics(case_id: str):
    return graph_metrics(case_id)
