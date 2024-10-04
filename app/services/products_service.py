from typing import Annotated

from fastapi import Depends, HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from starlette import status

from app.backend.db_depends import get_db
from app.models.product import Product
from app.schemas import InfoProduct
from app.services.users_service import get_current_user


class AllProducts:
    async def __call__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')
        return products.all()

class CreateProduct:
    async def __call__(self, db: Annotated[AsyncSession, Depends(get_db)], product_info: InfoProduct, get_user: Annotated[dict, Depends(get_current_user)]):
        if get_user.get('is_admin'):
            await db.execute(insert(Product).values(name=product_info.name,
                                      description=product_info.description,
                                      price=product_info.price,
                                      image_url=product_info.image_url,
                                      stock=product_info.stock,
                                      rating=0.0,
                                      slug=slugify(product_info.name)))
            await db.commit()
            return {
                'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )

class GetProduct:
    async def __call__(self, db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
        product = await db.scalar(select(Product).where(Product.slug == product_slug))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no product')
        return product

class PutProduct:
    async def __call__(self, db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, product_info: InfoProduct, get_user):
        product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
        if not product_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )

        await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product update is successful'
        }


class DeleteProduct:
    async def __call__(self, db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, get_user: Annotated[dict, Depends(get_current_user)]):
        product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
        if product_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        if get_user.get('is_admin'):
            await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )

class ProductsService:
    def __init__(self):
        self.all_products = AllProducts()
        self.create_product = CreateProduct()
        self.get_product = GetProduct()
        self.put_product = PutProduct()
        self.delete_product = DeleteProduct()