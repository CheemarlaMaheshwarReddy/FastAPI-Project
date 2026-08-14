from fastapi import APIRouter, Query, HTTPException, Depends
from auth import get_current_user
from pydantic import BaseModel
from model import SessionLocal, Product, User, Vote
from sqlalchemy import func


router = APIRouter()

class VoteCcreate(BaseModel):
    direction: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str|None = None
    price: float
    quantity: int
    owner_id: int
    votes: int



@router.get("/", response_model=list[ProductResponse])
def get_products(
    skip: int=Query(0, ge=0), 
    limit: int=Query(10, ge=1, le=100)
    ):
    db = SessionLocal()
    products = (
    db.query(
        Product.id,
        Product.name,
        Product.price,
        Product.quantity,
        Product.owner_id,
        func.count(Vote.product_id).label("votes")
    )
    .outerjoin(
        Vote,
        Product.id == Vote.product_id
    )
    .group_by(
        Product.id,
        Product.name,
        Product.price,
        Product.quantity,
        Product.owner_id
    )
    .offset(skip)
    .limit(limit)
    .all()
)
    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "owner_id": product.owner_id,
            "votes": product.votes
        }
        for product in products
    ]

class ProductUpdate(BaseModel):
    name: str
    price: float
    quantity: int


@router.put("/{product_id}")
def update_product(product_id: int, product_data: ProductUpdate, user: User = Depends(get_current_user)):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    if product.owner_id != user.id:
        raise HTTPException(
         status_code=403,
        detail="Not authorized to modify this product" 
        )
    product.name = product_data.name
    product.price = product_data.price
    product.quantity = product_data.quantity
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, user: User = Depends(get_current_user)):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
            )
    if product.owner_id != user.id:
        raise HTTPException(
         status_code=403,
        detail="Not authorized to delete this product" 
        )
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.get("/me")
def get_user_products(user: User = Depends(get_current_user)):
    return user.products

@router.post("/{product_id}/vote")
def vote_product(
    product_id: int,
    vote_data: VoteCcreate,
    user: User = Depends(get_current_user)
    ):
    db = SessionLocal()
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    existing_vote = db.query(Vote).filter(
        Vote.user_id == user.id,
        Vote.product_id == product.id
        ).first()
    
    if vote_data.direction == 1:
        if existing_vote:
            raise HTTPException(
                status_code=409,
                detail="Product already liked"
            )
        new_vote = Vote(
            user_id=user.id,
            product_id=product.id
        )
        db.add(new_vote)
        db.commit()
        return {
            "message": "Product liked"
        }
    
    if vote_data.direction == 0:
        if existing_vote is None:
            raise HTTPException(    
                status_code=404,
                detail="Product is not liked"
                )
        db.delete(existing_vote)
        db.commit()
        return {
            "message": "Product unliked"
            }
    