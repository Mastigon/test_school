
class GetProduct:
    async def __call__(self):
        pass

class ProductsService:
    def __init__(self):
        self.get_product = GetProduct()
