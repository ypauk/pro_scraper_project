from pydantic import BaseModel, Field, field_validator

class QuoteModel(BaseModel):
    text: str = Field(..., min_length=5)
    author: str = Field(..., max_length=100)
    tags: list[str] = Field(default_factory=list)

    @field_validator('text', mode='before')
    @classmethod
    def clean_quotes(cls, v: str) -> str:
        """Очищає текст від специфічних символів лапок, якщо вони є"""
        if isinstance(v, str):
            # Видаляємо розумні лапки, які часто зустрічаються в тексті цитат
            return v.replace('“', '').replace('”', '').strip()
        return v

class ScraperResult(BaseModel):
    """Модель для списку цитат та метаінформації"""
    total_found: int
    items: list[QuoteModel]