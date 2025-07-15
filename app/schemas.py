from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, datetime
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class MessageBase(BaseModel):
    id: int
    text: str = Field(..., max_length=1000)
    date: datetime
    channel: str
    has_media: bool

class ChannelStats(BaseModel):
    date: date
    message_count: int = Field(..., ge=0)
    media_count: int = Field(..., ge=0)
    unique_products: int = Field(..., ge=0)

class ProductMention(BaseModel):
    product_name: str = Field(..., min_length=2)
    count: int = Field(..., ge=1)
    last_mentioned: datetime
    channels: List[str]

class DetectedObject(BaseModel):
    object_class: str
    count: int
    confidence_avg: float = Field(..., ge=0, le=1)
    last_detected: datetime

class ImageAnalysis(BaseModel):
    top_classes: List[DetectedObject]
    total_detections: int
    processing_time: Optional[float]

class APIHealthCheck(BaseModel):
    status: HealthStatus
    db_connected: bool
    yolo_ready: bool
    last_scrape_time: Optional[datetime]
    active_connections: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime = Field(default_factory=datetime.now)

class SearchQuery(BaseModel):
    term: str = Field(..., min_length=2)
    start_date: Optional[date]
    end_date: Optional[date]
    channel: Optional[str]

class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class TopProducts(BaseModel):
    product_name: str
    mention_count: int
