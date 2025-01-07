"""
Run with this command: 

```
bazel run :fastapi -- dev server/v1/app.py
```

or

```
source .venv/bin/activate
fastapi dev server/v1/app.py
```
"""

from fastapi import FastAPI

from server.v1.config import ROOT_PREFIX
from lib.data_structures import Point

print(Point(100, 100))
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get(f"{ROOT_PREFIX}/join")
def get_join():
    return {"Hello": "World"}
