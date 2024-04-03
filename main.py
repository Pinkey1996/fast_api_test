from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geopy.distance import geodesic

# Database connection URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a session local object for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for declarative class definitions
Base = declarative_base()


# Define the Address model
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)


# Create the FastAPI application instance
app = FastAPI()

# Create tables in the database if they don't exist
Base.metadata.create_all(bind=engine)


# Helper function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request and response bodies
class AddressCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class AddressUpdate(BaseModel):
    name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


# Endpoint to create a new address
@app.post("/addresses/", response_model=AddressCreate)
def create_address(address: AddressCreate, db: SessionLocal = Depends(get_db)):
    db_address = Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


# Endpoint to retrieve an address by ID
@app.get("/addresses/{address_id}", response_model=AddressCreate)
def read_address(address_id: int, db: SessionLocal = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


# Endpoint to update an existing address
@app.put("/addresses/{address_id}", response_model=AddressUpdate)
def update_address(address_id: int, address: AddressUpdate, db: SessionLocal = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    for key, value in address.dict().items():
        if value is not None:
            setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address


# Endpoint to delete an address by ID
@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: SessionLocal = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}


# Endpoint to retrieve addresses within a certain distance from a given point
@app.get("/addresses/within_distance/")
def addresses_within_distance(latitude: float, longitude: float, distance: float = Query(...),
                              db: SessionLocal = Depends(get_db)):
    addresses = db.query(Address).all()
    valid_addresses = []
    for address in addresses:
        if geodesic((latitude, longitude), (address.latitude, address.longitude)).meters <= distance:
            valid_addresses.append(address)
    return valid_addresses
