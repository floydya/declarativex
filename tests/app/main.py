# pragma: no cover
import asyncio
import json
import pathlib
import warnings
from typing import Optional, List, Type

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from .schemas import Comment, BaseComment, Todo, BaseTodo, Post, BasePost

app = FastAPI()

with open(pathlib.Path(__file__).parent / "fixtures" / "comments.json", "r") as f:
    comments = json.load(f)

with open(pathlib.Path(__file__).parent / "fixtures" / "todos.json", "r") as f:
    todos = json.load(f)

with open(pathlib.Path(__file__).parent / "fixtures" / "posts.json", "r") as f:
    posts = json.load(f)


mapping = {
    "posts": (Post, BasePost, "userId", posts),
    "comments": (Comment, BaseComment, "postId", comments),
    "todos": (Todo, BaseTodo, "userId", todos),
}


def functions_factory(
    key: str,
    model: Type[BaseModel],
    base_model: Type[BaseModel],
    filter_field: str,
    db: List[dict],
):
    @app.get(f"/{key}", response_model=List[model])
    def mock_get(
        key_: Optional[int] = Query(default=None, alias=filter_field)
    ):
        return (
            db
            if key_ is None
            else [entity for entity in db if entity[filter_field] == key_]
        )

    mock_get.__name__ = f"mock_get_{key}"

    @app.post(f"/{key}", response_model=model)
    def mock_post(entity: base_model) -> model:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return model(**entity.dict(), id=len(db) + 1)

    mock_post.__name__ = f"mock_post_{key}"

    @app.get(f"/{key}/{{id}}", response_model=model)
    def mock_get_by_id(id: int):
        try:
            return db[id - 1]
        except IndexError:
            raise HTTPException(status_code=404, detail="Not found")

    mock_get_by_id.__name__ = f"mock_get_{key}_by_id"

    @app.put(f"/{key}/{{id}}", response_model=model)
    def mock_put(id: int, entity: base_model):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return {"id": id, **entity.dict()}
        except IndexError:
            raise HTTPException(status_code=404, detail="Not found")

    mock_put.__name__ = f"mock_put_{key}"

    @app.delete(f"/{key}/{{id}}")
    def mock_delete(id: int):
        try:
            _ = db[id - 1]
            return {}
        except IndexError:
            raise HTTPException(status_code=404, detail="Not found")

    mock_delete.__name__ = f"mock_delete_{key}"

    @app.patch(f"/{key}/{{id}}", response_model=model)
    def mock_patch(id: int, entity: base_model):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return {**db[id - 1], **entity.dict()}
        except IndexError:
            raise HTTPException(status_code=404, detail="Not found")

    mock_patch.__name__ = f"mock_patch_{key}"

    return [
        mock_get,
        mock_post,
        mock_get_by_id,
        mock_put,
        mock_delete,
        mock_patch,
    ]


for key_, args in mapping.items():
    functions_factory(key_, *args)


@app.get("/query")
def mock_query(query_param_1=Query(...), query_param_2=Query(...)):
    return {
        "query_param_1": query_param_1,
        "query_param_2": query_param_2,
    }


@app.get("/delay/{delay}")
async def mock_delay(delay: int, query_delay: Optional[int] = Query(default=None)):
    await asyncio.sleep(delay)
    return {
        "delay": delay,
        "query_delay": query_delay,
    }


@app.post("/status/{status_code}")
def mock_http_exception(status_code: int, response_body: dict):
    raise HTTPException(status_code=status_code, detail=response_body)
