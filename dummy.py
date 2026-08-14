from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

products = [
        {
        "id": 1,
        "name": "Laptop",
        "price": 60000,
        "quantity": 5
    },
    {
        "id": 2,
        "name": "Mouse",
        "price": 1000,
        "quantity": 20
    }
]

@app.post("/product", status_code = status.HTTP_201_CREATED)
def create_product(item: Product):
    products.append(item.model_dump())
    return {
        "message": "Product created",  
        "products": item
        }

@app.get("/product/{product_id}", status_code = status.HTTP_404_NOT_FOUND)
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "message": "Product found",
                "product": product
            }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="Product not found")


@app.put("/product/{product_id}")
def update_product(product_id: int, item: Product):
    for product in products:
        if product["id"] == product_id:
            product.update(item.model_dump())

            return {
                "message": "Product updated",
                "product": product
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found"
    )

@app.delete("/product/{product_id}", 
            status_code = status.HTTP_204_NO_CONTENT)

def delete_products(product_id: int):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return 
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found"
    )