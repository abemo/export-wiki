"""
Backend for export-wiki, responsible for managing users, tokens
and uploading resumes, and creating and returning cover letters
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO remove
items = []


class Item(BaseModel):
    name: str
    description: str


# create an item
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item


# get an item
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


# update an item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    items[item_id] = item
    return item


# Delete an item
@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = items.pop(item_id)
    return deleted_item


class Count(BaseModel):
    count: int


count = 0


# get the count
@app.get("/count/", response_model=Count)
async def get_count():
    return {"count": count}


# update an item
@app.put("/count/increment", response_model=Count)
async def increment_count():
    global count
    count += 1
    return {"count": count}


@app.get("/")
def read_root():
    return {"Hello": "World"}
