import pytest

from src.core import models
from src.tests import utils


@pytest.mark.public
@pytest.mark.anyio
async def test_get_meme(client, meme_factory):
    sa_object, data = meme_factory(qty=1)[0]
    async with client:
        response = await client.get(f'/api/v1/memes/{sa_object.id}')
    assert response.status_code == 200
    assert response.json() == {**data, 'id': sa_object.id}

@pytest.mark.public
@pytest.mark.anyio
@pytest.mark.parametrize('qty', [1, 2, 50])
async def test_get_memes(client, meme_factory, qty):
    memes_data: list[tuple[models.Meme, dict]] = meme_factory(qty=qty)
    async with client:
        response = await client.get(f'/api/v1/memes')
    assert response.status_code == 200
    expected_data = {
        'total': qty,
        'page': 1,
        'pages': qty//51 + 1,
        'size': 50,
        'items': [
            {**data, 'id': sa_object.id} for sa_object, data in memes_data
        ]
    }
    assert utils.ordered(response.json()) == utils.ordered(expected_data)
