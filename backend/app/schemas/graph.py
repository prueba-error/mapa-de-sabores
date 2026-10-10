from pydantic import BaseModel
from typing import List

class GraphNode(BaseModel):
    id: int
    name: str
    category: str
    color_code: str

class GraphEdge(BaseModel):
    ingredient_a_id: int
    ingredient_b_id: int
    affinity_score: float
    mechanism: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
