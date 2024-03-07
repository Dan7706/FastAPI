from fastapi import FastAPI, HTTPException, Depends, Path, Body
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional, Union
from bson import ObjectId

app = FastAPI()


@app.get("/")
async def index():
    return {"title": "Hello From FastAPI"}


class Item(BaseModel):
    # _id: str
    name: str
    description: Union[str, List, int] = None


# Connect to MongoDB
client = MongoClient("mongodb://mongo-db:27017")
db = client.mydatabase  # Replace "mydatabase" with your desired database name
collection = db.items    # Replace "items" with your desired collection name


@app.post("/items/", response_model=Item)
async def create_item(name: str, description: str):
    # Insert an item into MongoDB
    item_data = {"name": name, "description": description}
    result = collection.insert_one(item_data)
    return {"name": item_data["name"], "description": item_data["description"], "_id": str(result.inserted_id)}


@app.get("/items/", response_model=List[Item])
async def read_items():
    # Retrieve all items from MongoDB
    items = list(collection.find())
    print(items)
    return items



@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    # Retrieve a specific item from MongoDB
    obj_id = ObjectId(item_id)
    item = collection.find_one({"_id": obj_id}, {"_id": 1, "name": 1, "description": 1})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item



class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Union[str, List, int] = None

class ItemUpdateResponse(BaseModel):
    modified_count: int

@app.put("/items/{item_id}", response_model=ItemUpdateResponse)
def update_item(
    item_id: str = Path(..., title="The _id of the item to update"),
    update_data: ItemUpdate = Body(..., title="Data to update")):
    # Convert item_id to ObjectId
    obj_id = ObjectId(item_id)
    # Create the update query based on the provided data
    update_query = {"$set": update_data.dict(exclude_unset=True)}
    # Update the item in MongoDB
    result = collection.update_one({"_id": obj_id}, update_query)
    # Check if the item was found and updated
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Item with _id {item_id} not found")
    # Return the number of modified items
    return {"modified_count": result.modified_count}






@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    obj_id = ObjectId(item_id)
    if collection.find_one({"_id": obj_id}):
        collection.delete_one({"_id": obj_id})
        return f"{obj_id} deleted!"
    return f"{obj_id} already deleted!"




