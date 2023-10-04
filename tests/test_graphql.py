import pytest
from pydantic import BaseModel

from declarativex import BaseClient
from declarativex.methods import gql


class ExampleQuery(BaseModel):
    class Data(BaseModel):
        class Company(BaseModel):
            ceo: str

        class Roadster(BaseModel):
            apoapsis_au: float

        company: Company
        roadster: Roadster

    data: Data


class SpaceX(BaseClient):
    base_url = "https://spacex-production.up.railway.app/"

    @gql(
        """
        query ExampleQuery {
          company {
            ceo
          }
          roadster {
            apoapsis_au
          }
        }
        """
    )
    async def example_query(self) -> ExampleQuery:
        pass

    @gql(
        """
        query ($name: String!) {
          __type(name: $name) {
           name
          }
        }
        """
    )
    async def get_type(self, name: str) -> dict:
        pass


space_x = SpaceX()


@pytest.mark.asyncio
async def test_example_query():
    response = await space_x.example_query()
    assert isinstance(response, ExampleQuery)
    assert isinstance(response.data, ExampleQuery.Data)
    assert isinstance(response.data.company, ExampleQuery.Data.Company)
    assert isinstance(response.data.roadster, ExampleQuery.Data.Roadster)
    assert isinstance(response.data.company.ceo, str)
    assert response.data.company.ceo == "Elon Musk"
    assert isinstance(response.data.roadster.apoapsis_au, float)


@pytest.mark.asyncio
async def test_get_type():
    response = await space_x.get_type("users")
    assert isinstance(response, dict)
    assert response == {"data": {"__type": {"name": "users"}}}
