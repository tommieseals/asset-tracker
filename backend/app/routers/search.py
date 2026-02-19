"""AI-powered search endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import httpx
import json
import re
from ..database import get_db
from ..models import Asset, User, AssetStatus, AssetCategory
from ..schemas import SearchQuery, AISearchQuery, AssetResponse, SearchResult
from ..auth import get_current_user
from ..config import settings

router = APIRouter()

SEARCH_PROMPT = """You are a search query parser for an asset inventory system.
Given a natural language query, extract the search parameters.

Asset categories: laptop, monitor, keyboard, mouse, headset, phone, license, key, other
Asset statuses: available, checked_out, maintenance, retired

Respond with a JSON object containing:
- keywords: list of search keywords
- category: asset category if mentioned (or null)
- status: asset status if mentioned (or null)  
- department: department name if mentioned (or null)
- assigned_to_name: person name if mentioned (or null)
- unassigned: true if looking for unassigned assets

Now parse this query:
"""

async def parse_query_with_ai(query: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_API_URL}/chat/completions",
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "Output valid JSON only."},
                        {"role": "user", "content": SEARCH_PROMPT + f'"{query}"'}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                },
                headers={"Authorization": f"Bearer {settings.AI_API_KEY}"}
            )
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
    except Exception as e:
        print(f"AI search error: {e}")
    return {"keywords": query.split(), "category": None, "status": None, 
            "department": None, "assigned_to_name": None, "unassigned": False}

@router.post("/ai", response_model=SearchResult)
async def ai_search(
    search_query: AISearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    params = await parse_query_with_ai(search_query.query)
    query = select(Asset).options(selectinload(Asset.assignee))
    conditions = []
    
    if params.get("category"):
        try:
            conditions.append(Asset.category == AssetCategory(params["category"]))
        except ValueError:
            pass
    if params.get("status"):
        try:
            conditions.append(Asset.status == AssetStatus(params["status"]))
        except ValueError:
            pass
    for keyword in params.get("keywords", []):
        conditions.append(or_(
            Asset.name.ilike(f"%{keyword}%"),
            Asset.description.ilike(f"%{keyword}%"),
            Asset.manufacturer.ilike(f"%{keyword}%")
        ))
    if params.get("department"):
        subq = select(User.id).filter(User.department.ilike(f"%{params['department']}%"))
        conditions.append(Asset.assigned_to.in_(subq))
    if params.get("assigned_to_name"):
        subq = select(User.id).filter(User.full_name.ilike(f"%{params['assigned_to_name']}%"))
        conditions.append(Asset.assigned_to.in_(subq))
    if conditions:
        query = query.filter(and_(*conditions))
    
    result = await db.execute(query.limit(50))
    assets = result.scalars().all()
    return SearchResult(assets=assets, total=len(assets), query_interpretation=json.dumps(params))

@router.get("/", response_model=SearchResult)
async def basic_search(
    q: str,
    category: Optional[AssetCategory] = None,
    status: Optional[AssetStatus] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Asset).options(selectinload(Asset.assignee))
    if q:
        query = query.filter(or_(
            Asset.name.ilike(f"%{q}%"),
            Asset.description.ilike(f"%{q}%"),
            Asset.asset_tag.ilike(f"%{q}%"),
            Asset.serial_number.ilike(f"%{q}%")
        ))
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    result = await db.execute(query.limit(limit))
    assets = result.scalars().all()
    return SearchResult(assets=assets, total=len(assets))
