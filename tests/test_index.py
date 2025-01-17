from pathlib import Path
from tempfile import NamedTemporaryFile
from followthemoney import model
from nomenklatura.index import Index
from nomenklatura.index.tokenizer import Tokenizer

DAIMLER = "66ce9f62af8c7d329506da41cb7c36ba058b3d28"


def test_index_build(dloader):
    index = Index(dloader)
    assert len(index) == 0, index.terms
    assert len(index.fields) == 0, index.fields
    index.build()
    assert len(index) == 184, len(index)


def test_index_persist(dloader, dindex):
    with NamedTemporaryFile("w") as fh:
        path = Path(fh.name)
        dindex.save(path)
        loaded = Index.load(dloader, path)
    assert len(dindex.entities) == len(loaded.entities), (dindex, loaded)
    assert len(dindex) == len(loaded), (dindex, loaded)

    path.unlink(missing_ok=True)
    empty = Index.load(dloader, path)
    assert len(empty) == len(loaded), (empty, loaded)


def test_index_search(dindex):
    query = model.make_entity("Person")
    query.add("name", "Susanne Klatten")
    results = list(dindex.match_entities(query))
    assert len(results), len(results)
    first = results[0][0]
    assert first.schema == query.schema, first.schema
    assert "Klatten" in first.caption

    query = model.make_entity("Person")
    query.add("name", "Henry Ford")
    results = list(dindex.match(query))
    assert len(results), len(results)

    query = model.make_entity("Company")
    query.add("name", "Susanne Klatten")
    results = list(dindex.match_entities(query))
    assert len(results), len(results)
    first = results[0][0]
    assert first.schema != model.get("Person")
    assert "Klatten" not in first.caption

    query = model.make_entity("Address")
    matchies = [s.name for s in query.schema.matchable_schemata]
    assert "Person" not in matchies, matchies
    assert len(matchies) == 1, matchies
    query.add("full", "Susanne Klatten")
    for entity, _ in dindex.match_entities(query):
        assert entity.schema.name == "Address"


def test_index_pairs(dloader, dindex: Index):
    pairs = dindex.pairs()
    assert len(pairs) > 0, pairs
    tokenizer = dindex.tokenizer
    pair, score = pairs[0]
    entity0 = dloader.get_entity(str(pair[0]))
    tokens0 = set(tokenizer.entity(entity0, fuzzy=False))
    entity1 = dloader.get_entity(str(pair[1]))
    tokens1 = set(tokenizer.entity(entity1, fuzzy=False))
    overlap = tokens0.intersection(tokens1)
    assert len(overlap) > 0, overlap
    # assert "Schnabel" in (overlap, tokens0, tokens1)
    # assert "Schnabel" in (entity0.caption, entity1.caption)
    assert score > 0
    # assert False


def test_index_filter(dloader, dindex):
    query = dloader.get_entity(DAIMLER)
    query.id = None
    query.schema = model.get("Person")

    results = list(dindex.match_entities(query))
    for result, _ in results:
        assert not result.schema.is_a("Organization"), result.schema
