from typing import Literal 
from pydantic import BaseModel

class UserFilterQuery(BaseModel):
    cv_id: str | None
    salary: int | None
    filter_salary_mode: Literal['min', 'max', 'range'] | None
    district: str | None
    province: str | None
    salary_min: int | None
    salary_max: int | None