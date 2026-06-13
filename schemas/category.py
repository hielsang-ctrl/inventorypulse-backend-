class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None