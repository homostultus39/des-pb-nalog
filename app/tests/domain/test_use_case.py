import pytest
from domain.use_cases.search_directors import SearchDirectorsUseCase
from domain.use_cases.exceptions import CaptchaRequiredError
from tests.conftest import FakePbNalogClient, make_person, make_organization


@pytest.mark.asyncio
async def test_successful_collection_single_person_single_org():
    client = FakePbNalogClient()
    person = make_person()
    org = make_organization()
    client.persons_by_query["Займидорога"] = [person]
    client.orgs_by_token[person.token] = [org]

    use_case = SearchDirectorsUseCase(client)
    result = await use_case.execute("Займидорога")

    assert result.success is True
    assert result.error is None
    assert result.total == 1
    assert result.entities[0].person == person
    assert result.entities[0].organization == org


@pytest.mark.asyncio
async def test_no_persons_found_returns_empty_success():
    client = FakePbNalogClient()
    use_case = SearchDirectorsUseCase(client)

    result = await use_case.execute("Несуществующий директор")

    assert result.success is True
    assert result.total == 0
    assert result.entities == []


@pytest.mark.asyncio
async def test_multiple_persons_produce_flat_entities_list():
    client = FakePbNalogClient()
    p1, p2 = make_person(token="test_token_1"), make_person(token="test_token2", inn="111111")
    client.persons_by_query["Займидорога"] = [p1, p2]
    client.orgs_by_token["test_token_1"] = [make_organization(inn="101010"), make_organization(inn="121212")]
    client.orgs_by_token["test_token2"] = [make_organization(inn="111111")]

    use_case = SearchDirectorsUseCase(client)
    result = await use_case.execute("Займидорога")

    assert result.total == 3
    assert {e.organization.inn for e in result.entities} == {"101010", "121212", "111111"}


@pytest.mark.asyncio
async def test_captcha_on_one_person_does_not_fail_whole_request():
    """частичный успех"""
    client = FakePbNalogClient()
    p1, p2 = make_person(token="test_token_1"), make_person(token="test_token_2", inn="111111")
    client.persons_by_query["Займидорога"] = [p1, p2]
    client.orgs_by_token["test_token_1"] = [make_organization()]
    client.raise_on_token["test_token_2"] = CaptchaRequiredError("капча")

    use_case = SearchDirectorsUseCase(client)
    result = await use_case.execute("Займидорога")

    assert result.success is True
    assert result.total == 1
    assert result.entities[0].person == p1


@pytest.mark.asyncio
async def test_sla_timeout_returns_failure_without_hanging():
    client = FakePbNalogClient()
    client.persons_by_query["Займидорога"] = [make_person()]
    client.search_delay = 0.5

    use_case = SearchDirectorsUseCase(client, timeout=0.1)
    result = await use_case.execute("Займидорога")

    assert result.success is False
    assert "timeout" in result.error.lower()
    assert result.total == 0