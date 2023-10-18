from typing import Annotated

import pytest

from declarativex import http, FormField, FormData


@pytest.mark.asyncio
async def test_form_field():
    data = {"form_field": "testData12345", "another_field": "testData67890"}

    @http("POST", "/post", base_url="https://httpbin.org/")
    async def endpoint(
        form_field: Annotated[str, FormField],
        another_field: Annotated[str, FormField],
    ) -> dict:
        pass

    response = await endpoint(
        form_field=data["form_field"], another_field=data["another_field"]
    )
    assert response["form"]["form_field"] == data["form_field"]
    assert response["form"]["another_field"] == data["another_field"]


@pytest.mark.asyncio
async def test_form_data():
    data = {"form_field": "testData12345", "another_field": "testData67890"}

    @http("POST", "/post", base_url="https://httpbin.org/")
    async def endpoint(
        form: Annotated[dict, FormData],
    ) -> dict:
        pass

    response = await endpoint(form=data)
    assert response["form"]["form_field"] == data["form_field"]
    assert response["form"]["another_field"] == data["another_field"]
