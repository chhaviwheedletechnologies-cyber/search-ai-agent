from pydantic import BaseModel

class BusinessContext(BaseModel):

    business:str
    industry:str
    website:str
    location:str