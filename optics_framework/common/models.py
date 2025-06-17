from uuid import uuid4
from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from pydantic import BaseModel, Field

# State Enum
class State(str, Enum):
    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    COMPLETED_PASSED = "COMPLETED_PASSED"
    COMPLETED_FAILED = "COMPLETED_FAILED"
    RETRYING = "RETRYING"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

# Node Base Class
class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    state: State = State.NOT_RUN
    attempt_count: int = 0
    max_attempts: int = 3
    last_failure_reason: Optional[str] = None

# Linked List Nodes
class KeywordNode(Node):
    params: List[str] = Field(default_factory=list)
    method_ref: Optional[Callable] = None
    next: Optional['KeywordNode'] = None


class ModuleNode(Node):
    keywords_head: Optional[KeywordNode] = None
    next: Optional['ModuleNode'] = None


class TestCaseNode(Node):
    modules_head: Optional[ModuleNode] = None
    next: Optional['TestCaseNode'] = None


class RequestConfig(BaseModel):
    method: str
    query_params: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None


class ExpectedResult(BaseModel):
    expected_status: int
    expected_json: Optional[Dict[str, Any]] = None
    extract: Optional[Dict[str, str]] = None


class ErrorHandling(BaseModel):
    retry: int = 1
    timeout: int = 5000


class APICollection(BaseModel):
    name: str
    description: str
    endpoint: str
    request: RequestConfig
    expected_result: Optional[ExpectedResult] = None
    error_handling: Optional[ErrorHandling] = None


class APIData(BaseModel):
    api: Dict[str, APICollection] = Field(default_factory=dict)


class ElementData(BaseModel):
    elements: Dict[str, str] = Field(default_factory=dict)
    api_data: APIData = Field(default_factory=APIData)
