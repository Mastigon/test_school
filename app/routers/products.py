from fastapi import APIRouter

router = APIRouter(prefix='/products', tags=['products'])

router.get('/')
async def all_products():
    pass