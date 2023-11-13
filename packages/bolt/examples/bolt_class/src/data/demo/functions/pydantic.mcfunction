from pydantic import BaseModel

class Model(BaseModel, frozen=True):
  a: int
  b: str

say Model(a="123", b="123").json()
