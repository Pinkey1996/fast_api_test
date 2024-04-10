from pydantic import BaseModel, confloat, Field
from typing import List, Optional


# Pydantic models for request and response bodies
class AddressCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class AddressUpdate(BaseModel):
    name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class Coordinates(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)


class QueryParams(BaseModel):
    coordinates: Coordinates
    distance: float = Field(..., gt=0)


class AddressCreateWithValidation(AddressCreate):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)

