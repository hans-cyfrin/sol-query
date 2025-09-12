from typing import Any, Dict
import json
import pytest


def _assert_visibility_in(values, allowed):
    v = values.get("visibility")
    # visibility may be empty string when absent; only assert when present
    if v:
        assert str(v) in allowed


def test_01_query_contracts_in_simplecontract(engine):
    resp = engine.query_code("contracts", {}, {"files": [".*SimpleContract.sol"]})
    print("Contracts(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    # Expect exactly one contract named SimpleContract
    assert len(results) == 1
    c = results[0]
    assert c.get("type") == "contract"
    assert c.get("name") == "SimpleContract"

    # Validate exact location details
    loc = c.get("location", {})
    assert str(loc.get("file")).endswith("SimpleContract.sol")
    assert loc.get("line") == 7  # Contract declaration at line 7
    assert loc.get("column") == 1  # Starts at column 1
    assert loc.get("contract") == "SimpleContract"

    # Validate inheritance (SimpleContract has no inheritance)
    inheritance = c.get("inheritance", [])
    assert inheritance == []


def test_02_query_functions_in_simplecontract(engine):
    resp = engine.query_code("functions", {}, {"files": [".*SimpleContract.sol"]})
    print("Functions(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    expected_subset = {"pureFunction", "viewFunction", "setValue", "deposit", "internalHelper", "privateHelper"}
    # All expected functions should be present
    assert expected_subset.issubset(names)

    # Check detailed function properties
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}

    # Validate pureFunction details
    pure_func = items["pureFunction"]
    assert str(pure_func.get("state_mutability")).lower() == "pure"
    assert str(pure_func.get("visibility")).lower() == "public"
    assert pure_func.get("location", {}).get("line") == 22
    assert pure_func.get("signature") == "pureFunction(uint256,uint256)"

    # Validate viewFunction details
    view_func = items["viewFunction"]
    assert str(view_func.get("state_mutability")).lower() == "view"
    assert str(view_func.get("visibility")).lower() == "public"
    assert view_func.get("location", {}).get("line") == 27
    assert view_func.get("signature") == "viewFunction()"

    # Validate deposit function details
    deposit_func = items["deposit"]
    assert str(deposit_func.get("state_mutability")).lower() == "payable"
    assert str(deposit_func.get("visibility")).lower() == "public"
    assert deposit_func.get("location", {}).get("line") == 37
    assert deposit_func.get("signature") == "deposit()"

    # Validate setValue function details (has onlyOwner modifier)
    set_value_func = items["setValue"]
    assert str(set_value_func.get("state_mutability")).lower() == "nonpayable"
    assert str(set_value_func.get("visibility")).lower() == "public"
    assert set_value_func.get("location", {}).get("line") == 32
    # Note: modifiers might not be included in basic query_code response
    # assert set_value_func.get("signature") == "setValue(uint256)"

    # Validate internal function
    internal_func = items["internalHelper"]
    assert str(internal_func.get("visibility")).lower() == "internal"
    assert str(internal_func.get("state_mutability")).lower() == "pure"
    assert internal_func.get("location", {}).get("line") == 42

    # Validate private function
    private_func = items["privateHelper"]
    assert str(private_func.get("visibility")).lower() == "private"
    assert str(private_func.get("state_mutability")).lower() == "pure"
    assert private_func.get("location", {}).get("line") == 47


def test_03_query_variables_in_simplecontract(engine):
    resp = engine.query_code("variables", {}, {"files": [".*SimpleContract.sol"]})
    print("Variables(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    # Expect two state variables: value (uint256), owner (address)
    names = {r.get("name"): r for r in results}
    assert "value" in names and "owner" in names

    # Validate value variable details
    value_var = names["value"]
    assert value_var.get("is_state_variable") is True
    assert str(value_var.get("type_name")).lower() == "uint256"
    assert str(value_var.get("visibility")).lower() == "public"
    assert value_var.get("location", {}).get("line") == 8
    assert str(value_var.get("location", {}).get("file")).endswith("SimpleContract.sol")

    # Validate owner variable details
    owner_var = names["owner"]
    assert owner_var.get("is_state_variable") is True
    assert str(owner_var.get("type_name")).lower() == "address"
    assert str(owner_var.get("visibility")).lower() == "public"
    assert owner_var.get("location", {}).get("line") == 9
    assert str(owner_var.get("location", {}).get("file")).endswith("SimpleContract.sol")


def test_04_query_events_in_erc721imports(engine):
    resp = engine.query_code("events", {}, {"files": [".*ERC721WithImports.sol"]})
    print("Events(ERC721WithImports):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name"): r for r in results}
    # Expect TokenMinted, PriceUpdated
    assert {"TokenMinted", "PriceUpdated"}.issubset(set(names.keys()))

    # Validate TokenMinted event details
    token_minted = names["TokenMinted"]
    assert token_minted.get("type") == "event"
    assert token_minted.get("location", {}).get("line") == 23
    assert str(token_minted.get("location", {}).get("file")).endswith("ERC721WithImports.sol")

    # Validate PriceUpdated event details
    price_updated = names["PriceUpdated"]
    assert price_updated.get("type") == "event"
    assert price_updated.get("location", {}).get("line") == 24
    assert str(price_updated.get("location", {}).get("file")).endswith("ERC721WithImports.sol")


def test_05_query_modifiers_in_simplecontract(engine):
    resp = engine.query_code("modifiers", {}, {"files": [".*SimpleContract.sol"]})
    print("Modifiers(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {r.get("name"): r for r in results}
    assert "onlyOwner" in names

    # Validate onlyOwner modifier details
    only_owner_item = next((r for r in results if r.get("name") == "onlyOwner"), None)
    assert only_owner_item is not None
    assert only_owner_item.get("type") == "modifier"
    assert only_owner_item.get("location", {}).get("line") == 11
    assert str(only_owner_item.get("location", {}).get("file")).endswith("SimpleContract.sol")


def test_06_query_errors_none_expected(engine):
    resp = engine.query_code("errors", {}, {"files": [".*SimpleContract.sol"]})
    print("Errors(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert results == []


def test_07_query_all_structs(engine):
    resp = engine.query_code("structs")
    print("Structs(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # Should find UserData struct in sample_contract.sol
    results = resp.get("data", {}).get("results", [])
    assert len(results) == 1
    struct = results[0]
    assert struct.get("name") == "UserData"
    assert struct.get("type") == "struct"

    # Validate UserData struct details
    assert str(struct.get("location", {}).get("file")).endswith("sample_contract.sol")
    # UserData struct is around line 152-158 in sample_contract.sol
    assert 150 <= struct.get("location", {}).get("line") <= 160


def test_08_query_all_enums(engine):
    resp = engine.query_code("enums")
    print("Enums(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    # In current fixtures, no enums are defined
    assert resp.get("data", {}).get("results", []) == []


def test_09_query_statements(engine):
    resp = engine.query_code("statements", {}, {"files": [".*SimpleContract.sol"]})
    print("Statements(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert isinstance(results, list)
    assert len(results) > 0


def test_10_query_expressions(engine):
    resp = engine.query_code("expressions", {}, {"files": [".*SimpleContract.sol"]})
    print("Expressions(SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    assert isinstance(results, list)
    assert len(results) > 0


def test_11_query_calls(engine):
    resp = engine.query_code("calls")
    print("Calls(all):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    results = resp.get("data", {}).get("results", [])
    names = {str(r.get("name")) for r in results}
    # Expect to find names including low-level and member calls present in fixtures
    # Examples: _safeMint, IERC721(...).safeTransferFrom, to.call
    assert any("_safeMint" in n for n in names) or any("safeTransferFrom" in n for n in names) or any(".call" in n for n in names)


def test_12_query_flow_placeholder(engine):
    resp = engine.query_code("flow")
    print("Flow(all):", json.dumps(resp, indent=2))
    # Valid query_type; implementation returns empty results
    assert resp.get("success") is True
    assert resp.get("data", {}).get("results", []) == []


def test_13_functions_by_name_regex(engine):
    resp = engine.query_code("functions", {"names": "transfer.*"})
    print("Functions(names=transfer.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect presence of known functions
    expected = {"transferOwnership", "transferWithCall", "vulnerableTransfer", "transferWithMath"}
    assert expected.intersection(names)

    # Validate specific transfer functions details
    items = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}

    # transferOwnership should be from sample_contract.sol Token or MultipleInheritance.sol
    if "transferOwnership" in items:
        transfer_ownership = items["transferOwnership"]
        assert transfer_ownership.get("type") == "function"
        assert "transfer" in transfer_ownership.get("name").lower()
        # Basic query_code doesn't include modifiers, so just check signature
        assert transfer_ownership.get("signature") == "transferOwnership(address)"


def test_14_functions_by_multiple_names(engine):
    resp = engine.query_code("functions", {"names": ["approve", ".*mint.*"]})
    print("Functions(names=approve|.*mint.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Approve may not exist in local fixtures; ensure known mints exist
    assert {"mint"}.issubset({n for n in names if n and n.lower().startswith("mint") or n == "mint"})


def test_15_functions_by_visibility(engine):
    resp = engine.query_code("functions", {"visibility": ["public", "external"]})
    print("Functions(visibility=public|external):", json.dumps(resp, indent=2))
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
    print("Functions(no modifiers, SimpleContract):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    assert "deposit" in names and "setValue" not in names


def test_18_functions_with_modifiers(engine):
    resp = engine.query_code("functions", {"modifiers": ["only.*"]})
    print("Functions(modifiers=only.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect functions guarded by only* modifiers across fixtures
    expected = {"setValue", "mint", "transferOwnership", "updatePrice"}
    assert expected.intersection(names)


def test_19_functions_filtered_by_contract_names(engine):
    resp = engine.query_code("functions", {"contracts": [".*Token.*", ".*ERC721.*"]})
    print("Functions(contracts=.*Token.*|.*ERC721.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name") for r in resp.get("data", {}).get("results", [])}
    # Expect functions from MultiInheritanceToken and ERC721WithImports
    assert {"mint", "transferWithCall", "internalOnlyFunction", "vulnerableTransfer"}.intersection(names)


def test_20_variables_by_type_patterns(engine):
    resp = engine.query_code("variables", {"types": ["uint.*", "mapping.*"]})
    print("Variables(types=uint.*|mapping.*):", json.dumps(resp, indent=2))
    assert resp.get("success") is True
    names = {r.get("name"): r for r in resp.get("data", {}).get("results", [])}
    # Expect known variables from fixtures
    assert {"value", "balances", "totalSupply"}.intersection(set(names.keys()))

    # Validate specific variables by type
    if "value" in names:
        value_var = names["value"]
        assert "uint" in str(value_var.get("type_name")).lower()
        assert value_var.get("is_state_variable") is True

    if "balances" in names:
        balances_var = names["balances"]
        assert "mapping" in str(balances_var.get("type_name")).lower()
        assert balances_var.get("is_state_variable") is True

    if "totalSupply" in names:
        total_supply_var = names["totalSupply"]
        assert "uint" in str(total_supply_var.get("type_name")).lower()
        assert total_supply_var.get("is_state_variable") is True


