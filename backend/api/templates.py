"""
Template API endpoints for managing design templates.
"""
import os
import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger

from storage.database import get_session_direct, Template
from sqlalchemy import select, desc

router = APIRouter()


# ── Pydantic Models ──────────────────────────────────────

class TemplateResponse(BaseModel):
    id: str
    name: str
    type: str
    category: str
    dimensions: Optional[dict] = None
    preview_url: Optional[str] = None
    template_path: Optional[str] = None
    tags: List[str] = []
    usage_count: int = 0


class BackgroundInfo(BaseModel):
    filename: str
    path: str
    category: str
    size_kb: float


# ── Helper Functions ─────────────────────────────────────

def _parse_template(db_template) -> dict:
    """Convert database template to response dict."""
    dimensions = None
    if db_template.dimensions:
        try:
            dimensions = json.loads(db_template.dimensions)
        except:
            dimensions = None
    
    metadata = {}
    if db_template.metadata_json:
        try:
            metadata = json.loads(db_template.metadata_json)
        except:
            metadata = {}
    
    return {
        "id": db_template.id,
        "name": db_template.name,
        "type": db_template.type,
        "category": db_template.category,
        "dimensions": dimensions,
        "preview_url": db_template.preview_url,
        "template_path": db_template.template_path,
        "tags": metadata.get("tags", []),
        "usage_count": db_template.usage_count
    }


# ── API Endpoints ────────────────────────────────────────

@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    type: Optional[str] = Query(None, description="Filter by type: 'image' or 'video'"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, le=500),
    offset: int = Query(0)
):
    """List design templates with optional filtering."""
    session = await get_session_direct()
    try:
        query = select(Template).order_by(desc(Template.usage_count))
        
        if type:
            query = query.where(Template.type == type)
        if category:
            query = query.where(Template.category == category)
        
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        templates = result.scalars().all()
        
        return [_parse_template(t) for t in templates]
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


@router.get("/templates/popular", response_model=List[TemplateResponse])
async def get_popular_templates(
    limit: int = Query(20, le=100)
):
    """Get most-used templates."""
    session = await get_session_direct()
    try:
        query = select(Template).order_by(desc(Template.usage_count)).limit(limit)
        result = await session.execute(query)
        templates = result.scalars().all()
        
        return [_parse_template(t) for t in templates]
    except Exception as e:
        logger.error(f"Error getting popular templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template by ID."""
    session = await get_session_direct()
    try:
        result = await session.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return _parse_template(template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


@router.post("/templates/{template_id}/use")
async def use_template(template_id: str):
    """Increment template usage count."""
    session = await get_session_direct()
    try:
        result = await session.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template.usage_count += 1
        await session.commit()
        
        return {"status": "success", "usage_count": template.usage_count}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error incrementing usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


@router.get("/templates/backgrounds", response_model=List[BackgroundInfo])
async def get_backgrounds(
    category: Optional[str] = Query(None, description="Filter by category prefix")
):
    """Get available background templates from the library."""
    try:
        backgrounds_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'creative', 'data', 'outputs', 'backgrounds'
        )
        
        if not os.path.exists(backgrounds_dir):
            return []
        
        backgrounds = []
        for filename in os.listdir(backgrounds_dir):
            if not filename.endswith('.png'):
                continue
            
            # Extract category from filename (e.g., "bg_corporate_..." -> "corporate")
            parts = filename.replace('bg_', '').split('_')
            bg_category = parts[0] if parts else 'unknown'
            
            if category and not bg_category.startswith(category):
                continue
            
            file_path = os.path.join(backgrounds_dir, filename)
            size_kb = os.path.getsize(file_path) / 1024
            
            backgrounds.append(BackgroundInfo(
                filename=filename,
                path=f"/outputs/backgrounds/{filename}",
                category=bg_category,
                size_kb=round(size_kb, 1)
            ))
        
        # Sort by category then filename
        backgrounds.sort(key=lambda x: (x.category, x.filename))
        
        return backgrounds
    except Exception as e:
        logger.error(f"Error listing backgrounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))
