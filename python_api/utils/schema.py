from typing import Literal 
from pydantic import BaseModel

class UserFilterQuery(BaseModel):
    cv_id: str | None
    salary: int | None = None
    filter_salary_mode: Literal['min', 'max', 'range'] | None
    district: str | None = None
    province: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None