from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import json
import os
import secrets
from email_utils import send_inquiry_email
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials


load_dotenv()
app = FastAPI()
security = HTTPBasic()
ADMIN_USERNAME = "harsh"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "harsh@0958")

# Add CORS middleware - THIS FIXES THE NETWORK ERROR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  # Your Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Product(BaseModel):
    id: int
    name: str
    price: float
    imageURL: str
    description: str

class Inquiry(BaseModel):
    name: str
    email: str
    phone: str
    message: str
    product_id: int

# Load products from JSON
def load_products():
    with open('products.json', 'r') as f:
        return json.load(f)

def save_products(products):
    with open('products.json', 'w') as f:
        json.dump(products, f, indent=2)

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise Exception("Invalid credentials")
    return True

# Admin endpoints with password protection
@app.post("/products", dependencies=[Depends(verify_admin)])
async def add_product(product: Product):
    products = load_products()
    # Ensure unique id
    if any(p['id'] == product.id for p in products):
        return JSONResponse(content={"status": "error", "message": "ID already exists"}, status_code=400)
    products.append(product.dict())
    save_products(products)
    return JSONResponse(content={"status": "success", "message": "Product added"}, status_code=201)


@app.put("/products/{product_id}", dependencies=[Depends(verify_admin)])
async def update_product(product_id: int, product: Product):
    products = load_products()
    for idx, p in enumerate(products):
        if p['id'] == product_id:
            products[idx] = product.dict()
            save_products(products)
            return JSONResponse(content={"status": "success", "message": "Product updated"}, status_code=200)
    return JSONResponse(content={"status": "error", "message": "Product not found"}, status_code=404)


@app.delete("/products/{product_id}", dependencies=[Depends(verify_admin)])
async def delete_product(product_id: int):
    products = load_products()
    new_products = [p for p in products if p['id'] != product_id]
    if len(new_products) == len(products):
        return JSONResponse(content={"status": "error", "message": "Product not found"}, status_code=404)
    save_products(new_products)
    return JSONResponse(content={"status": "success", "message": "Product deleted"}, status_code=200)

@app.get("/products")
async def get_products():
    """Get all products"""
    return JSONResponse(content=load_products(), status_code=200)

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get single product by ID"""
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return JSONResponse(
            content={"status": "error", "message": "Product not found"},
            status_code=404
        )
    return JSONResponse(content=product, status_code=200)

@app.post("/submit-inquiry")
async def submit_inquiry(inquiry: Inquiry, request: Request):
    try:
        # Get product details for email
        products = load_products()
        product = next((p for p in products if p['id'] == inquiry.product_id), None)
        
        if not product:
            return JSONResponse(
                content={"status": "error", "message": "Product not found"},
                status_code=404
            )
        
        # Send email
        send_inquiry_email(
            inquiry.name,
            inquiry.email,
            inquiry.phone,
            inquiry.message,
            product
        )
        
        # Always return success to frontend
        return JSONResponse(
            content={"status": "success", "message": "Inquiry submitted successfully!"},
            status_code=200
        )
        
    except Exception as e:
        # Log error but still return success to frontend
        print(f"Backend error: {e}")
        return JSONResponse(
            content={"status": "success", "message": "Inquiry submitted successfully!"},
            status_code=200
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)