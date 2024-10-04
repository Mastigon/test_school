from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.schemas import InfoProduct
from app.services.products_service import ProductsService
from app.services.users_service import get_current_user

router = APIRouter(prefix='/products', tags=['products'])

@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)], product_service: ProductsService = Depends()):
    return await product_service.all_products(db)

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], product_info: InfoProduct, get_user: Annotated[dict, Depends(get_current_user)], product_service: ProductsService = Depends()):
    return await product_service.create_product(db, product_info, get_user)


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, product_service: ProductsService = Depends()):
    return await product_service.get_product(db, product_slug)


@router.put('/update/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, product_info=InfoProduct, product_service: ProductsService = Depends()):
    return await product_service.put_product(db, product_slug, product_info)


@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, get_user: Annotated[dict, Depends(get_current_user)], product_service: ProductsService = Depends()):
    return await product_service.delete_product(db, product_slug, get_user)



