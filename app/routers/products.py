from fastapi import APIRouter, Depends

from app.services.products_service import ProductsService

router = APIRouter(prefix='/products', tags=['products'])

router.get('/')
async def all_products(product_service: Depends(ProductsService)):
    return await product_service.get_product()