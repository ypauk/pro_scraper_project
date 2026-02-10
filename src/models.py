from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List


class BookModel(BaseModel):
    title: str = Field(..., min_length=1)
    price: str = Field(...)
    availability: str = Field(...)
    rating: str = Field(...)
    image_url: str = Field(...)
    product_url: str = Field(...)

    @field_validator('price', mode='before')
    @classmethod
    def clean_price(cls, v: str) -> str:
        """Remove currency symbol (£) and extra whitespace from price"""
        if isinstance(v, str):
            # Remove pound sterling symbol for easier analytics
            return v.replace('£', '').strip()
        return v

    @field_validator('availability', mode='before')
    @classmethod
    def clean_availability(cls, v: str) -> str:
        """Keep only the main availability status"""
        if isinstance(v, str):
            # Website often returns "In stock (22 available)", simplify it
            if "In stock" in v:
                return "In Stock"
            return v.strip()
        return v

    @field_validator('rating', mode='before')
    @classmethod
    def convert_rating(cls, v: str | list) -> str:
        """Convert CSS-based rating (e.g. 'star-rating Three') to numeric value"""
        if isinstance(v, list):
            # Scrapy/BS4 may sometimes return a list of CSS classes
            v = " ".join(v)

        ratings_map = {
            'One': '1',
            'Two': '2',
            'Three': '3',
            'Four': '4',
            'Five': '5'
        }
        for word, num in ratings_map.items():
            if word in v:
                return num
        return "0"


class ScraperResult(BaseModel):
    """Model representing scraped books and related metadata"""
    total_found: int
    items: List[BookModel]
