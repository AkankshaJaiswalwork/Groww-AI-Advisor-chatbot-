from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Holding(BaseModel):
    company_name: str
    allocation_percentage: float
    sector: str

class MutualFund(BaseModel):
    fund_id: str
    fund_name: str
    category: str
    aum_cr: Optional[float] = None
    expense_ratio: Optional[float] = None
    returns_1y: Optional[float] = None
    returns_3y: Optional[float] = None
    returns_5y: Optional[float] = None
    risk_level: Optional[str] = None
    nav: Optional[float] = None
    pe_ratio: Optional[float] = None
    holdings: List[Holding] = []
    fund_manager: Optional[str] = None
    amc: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ScrapeResult(BaseModel):
    success: bool
    fund_id: str
    data: Optional[MutualFund] = None
    error: Optional[str] = None
