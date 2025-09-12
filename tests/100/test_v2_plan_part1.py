from typing import Any, Dict

import pytest


def _assert_visibility_in(values, allowed):
    v = values.get("visibility")
    # visibility may be empty string when absent; only assert when present
    if v:
        assert str(v) in allowed


def test_01_query_contracts_in_simplecontract(engine):
    resp = engine.query_code("contracts", {}, {"files": [".*SimpleContract.sol"]})
    print("Contracts(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    # Expect exactly one contract named SimpleContract
    assert len(results) == 1
    c = results[0]
    assert c.get("type") == "ContractDeclaration"
    assert c.get("name") == "SimpleContract"
    loc = c.get("location", {})
    assert str(loc.get("file")).endswith("SimpleContract.sol")


def test_02_query_functions_in_simplecontract(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]})
    print("Functions(SimpleContract):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    expected_subset = {"pureFunction", "viewFunction", "setValue", "deposit", "internalHelper", "privateHelper"}
    # All expected functions should be present
    assert expected_subset.issubset(names)
    # Check visibilities for a few known ones
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    assert str(items["pureFunction"].get("state_mutability")).lower() == "pure"
    assert str(items["viewFunction"].get("state_mutability")).lower() == "view"
    assert str(items["deposit"].get("state_mutability")).lower() == "payable"


def test_03_query_variables_in_simplecontract(engine):
    resp = engine.query_code("variables", {}, {"files": [".*SimpleContract.sol"]})
    print("Variables(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    # Expect two state variables: value (uint256), owner (address)
    names = {r.get("name"): r for r in results}
    assert "value" in names and "owner" in names
    assert names["value"].get("is_state_variable") is True
    assert names["owner"].get("is_state_variable") is True
    assert "uint" in str(names["value"].get("type_name")).lower()
    assert "address" in str(names["owner"].get("type_name")).lower()


def test_04_query_events_in_erc721imports(engine):
    resp = engine.query_code("events", {}, {"files": [".*ERC721WithImports.sol"]})
    print("Events(ERC721WithImports):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    # Expect TokenMinted, PriceUpdated
    assert {"TokenMinted", "PriceUpdated"}.issubset(names)


def test_05_query_modifiers_in_simplecontract(engine):
    resp = engine.query_code("modifiers", {}, {"files": [".*SimpleContract.sol"]})
    print("Modifiers(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name") for r in results}
    assert "onlyOwner" in names


def test_06_query_errors_none_expected(engine):
    resp = engine.query_code("errors", {}, {"files": [".*SimpleContract.sol"]})
    print("Errors(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert results == []


def test_07_query_all_structs(engine):
    resp = engine.query_code("structs")
    print("Structs(all):", resp)
    assert resp.get("success") is True
    # Should find UserData struct in sample_contract.sol
    results = resp.get("data", {}).get("results", [])
    assert len(results) == 1
    struct = results[0]
    assert struct.get("name") == "UserData"
    assert struct.get("type") == "StructDeclaration"


def test_08_query_all_enums(engine):
    resp = engine.query_code("enums")
    print("Enums(all):", resp)
    assert resp.get("success") is True
    # In current fixtures, no enums are defined
    assert resp.get("data", {}).get("results", []) == []


def test_09_query_statements(engine):
    resp = engine.query_code("statements", {}, {"files": [".*SimpleContract.sol"]})
    print("Statements(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert isinstance(results, list)
    assert len(results) > 0


def test_10_query_expressions(engine):
    resp = engine.query_code("expressions", {}, {"files": [".*SimpleContract.sol"]})
    print("Expressions(SimpleContract):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert isinstance(results, list)
    assert len(results) > 0


def test_11_query_calls(engine):
    resp = engine.query_code("calls")
    print("Calls(all):", resp)
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {str(r.get("name")) for r in results}
    # Expect to find names including low-level and member calls present in fixtures
    # Examples: _safeMint, IERC721(...).safeTransferFrom, to.call
    assert any("_safeMint" in n for n in names) or any("safeTransferFrom" in n for n in names) or any(".call" in n for n in names)


def test_12_query_flow_placeholder(engine):
    resp = engine.query_code("flow")
    print("Flow(all):", resp)
    # Valid query_type; implementation returns empty results
    assert resp.get("success") is True
    assert resp.get("data", {}).get("results", []) == []


def test_13_functions_by_name_regex(engine):
    resp = engine.query_code("functions", {"names": "transfer.*"})
    print("Functions(names=transfer.*):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect presence of known functions
    expected = {"transferOwnership", "transferWithCall", "vulnerableTransfer", "transferWithMath"}
    assert expected.intersection(names)


def test_14_functions_by_multiple_names(engine):
    resp = engine.query_code("functions", {"names": ["approve", ".*mint.*"]})
    print("Functions(names=approve|.*mint.*):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Approve may not exist in local fixtures; ensure known mints exist
    assert {"mint"}.issubset({n for n in names if n and n.lower().startswith("mint") or n == "mint"})


def test_15_functions_by_visibility(engine):
    resp = engine.query_code("functions", {"visibility": ["public", "external"]})
    print("Functions(visibility=public|external):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Spot-check presence of known public/external functions
    expected_subset = {"deposit", "viewFunction", "pureFunction", "publicFunction", "externalFunction", "mint"}
    assert expected_subset.intersection(names)


def test_16_functions_by_state_mutability_view(engine):
    resp = engine.query_code("functions", {"state_mutability": "view"})
    assert resp.get("success") is True
    for r in resp.get("data", {}).get("results", []):
        sm = str(r.get("state_mutability", "")).lower()
        if sm:
            assert sm == "view"


def test_17_functions_no_modifiers(engine):
    resp = engine.query_code("functions", {"modifiers": []}, {"files": [".*SimpleContract.sol"]})
    print("Functions(no modifiers, SimpleContract):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "deposit" in names and "setValue" not in names


def test_18_functions_with_modifiers(engine):
    resp = engine.query_code("functions", {"modifiers": ["only.*"]})
    print("Functions(modifiers=only.*):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect functions guarded by only* modifiers across fixtures
    expected = {"setValue", "mint", "transferOwnership", "updatePrice"}
    assert expected.intersection(names)


def test_19_functions_filtered_by_contract_names(engine):
    resp = engine.query_code("functions", {"contracts": [".*Token.*", ".*ERC721.*"]})
    print("Functions(contracts=.*Token.*|.*ERC721.*):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect functions from MultiInheritanceToken and ERC721WithImports
    assert {"mint", "transferWithCall", "internalOnlyFunction", "vulnerableTransfer"}.intersection(names)


def test_20_variables_by_type_patterns(engine):
    resp = engine.query_code("variables", {"types": ["uint.*", "mapping.*"]})
    print("Variables(types=uint.*|mapping.*):", resp)
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect known variables from fixtures
    assert {"value", "balances", "totalSupply"}.intersection(names)


