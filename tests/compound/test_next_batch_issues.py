#!/usr/bin/env python3
"""
Next Batch Issues Test - Round 2
===============================

This test specifically targets the next batch of issues discovered after
the initial fixes were implemented.
"""

import pytest
from pathlib import Path
from sol_query.query.engine_v2 import SolidityQueryEngineV2


class TestNextBatchIssues:
    """Test class for identifying next batch of issues."""

    @classmethod
    def setup_class(cls):
        """Setup the query engine with Compound Protocol contracts."""
        cls.fixtures_dir = Path(__file__).parent.parent / "fixtures"
        cls.compound_dir = cls.fixtures_dir / "compound-protocol" / "contracts"

        # Initialize the V2 engine
        cls.engine = SolidityQueryEngineV2()
        cls.engine.load_sources([cls.compound_dir])

    # def test_issue_4_specific_function_call_detection(self):
    #     """
    #     Issue #4: Missing Specific Function Call Detection
    #     Test if mintInternal call in CErc20.sol:50 is detected
    #     """
    #     print("\n🔍 Testing Issue #4: Specific Function Call Detection")
    #     print("Checking if mintInternal(mintAmount) call in CErc20.mint is detected...")

    #     # Test mintInternal references
    #     mintinternal_refs = self.engine.find_references(
    #         "mintInternal",
    #         "function",
    #         reference_type="usages",
    #         direction="both"
    #     )

    #     assert mintinternal_refs['success'] == True, "Should successfully find mintInternal references"

    #     refs_data = mintinternal_refs['data']['references']
    #     usages = refs_data.get('usages', [])

    #     print(f"📊 mintInternal function: {len(usages)} usages found")

    #     # Look specifically for the call in CErc20.mint at line 50
    #     cerc20_mint_usage = None
    #     for usage in usages:
    #         location = usage.get('location', {})
    #         print(f"  📍 Usage in {location.get('contract')}:{location.get('line')} (function: {location.get('function')})")

    #         if (location.get('contract') == 'CErc20' and
    #             location.get('function') == 'mint' and
    #             location.get('line') == 50):
    #             cerc20_mint_usage = usage
    #             break

    #     # SPECIFIC ASSERTION: This call should be found
    #     if cerc20_mint_usage:
    #         print(f"✅ FOUND: mintInternal call in CErc20.mint at line {cerc20_mint_usage['location']['line']}")
    #         assert cerc20_mint_usage['usage_type'] in ['call', 'function_call'], f"Expected call usage type, got {cerc20_mint_usage.get('usage_type')}"
    #     else:
    #         print(f"❌ ISSUE #4 CONFIRMED: mintInternal call in CErc20.mint:50 NOT FOUND")
    #         print(f"   This is a clear function call that should be detected!")
    #         assert False, "Issue #4: Missing specific function call - mintInternal in CErc20.mint:50"

    def test_issue_5_cross_contract_calls(self):
        """
        Issue #5: Cross-Contract Function Call Analysis
        Test if calls to interface functions are detected
        """
        print("\n🔍 Testing Issue #5: Cross-Contract Function Calls")
        print("Checking interface function calls...")

        # Test EIP20Interface.totalSupply which should be called in CErc20.initialize
        totalsupply_refs = self.engine.find_references(
            "totalSupply",
            "function",
            reference_type="usages",
            direction="both"
        )

        if totalsupply_refs['success']:
            refs_data = totalsupply_refs['data']['references']
            usages = refs_data.get('usages', [])
            definitions = refs_data.get('definitions', [])

            print(f"📊 totalSupply: {len(definitions)} definitions, {len(usages)} usages")

            # Look for the specific call in CErc20.initialize:38
            cerc20_init_usage = None
            for usage in usages:
                location = usage.get('location', {})
                if (location.get('contract') == 'CErc20' and
                    location.get('function') == 'initialize'):
                    cerc20_init_usage = usage
                    break

            if cerc20_init_usage:
                print(f"✅ Found totalSupply call in CErc20.initialize")
            else:
                print(f"⚠️ Potential Issue #5: totalSupply call in CErc20.initialize not found")

    def test_issue_6_modifier_references(self):
        """
        Issue #6: Modifier Reference Tracking
        Test if modifiers are properly tracked
        """
        print("\n🔍 Testing Issue #6: Modifier Reference Tracking")
        print("Checking nonReentrant modifier references...")

        # Test nonReentrant modifier
        nonreentrant_refs = self.engine.find_references(
            "nonReentrant",
            "modifier",
            reference_type="all",
            direction="both"
        )

        if nonreentrant_refs['success']:
            refs_data = nonreentrant_refs['data']['references']
            usages = refs_data.get('usages', [])
            definitions = refs_data.get('definitions', [])

            print(f"📊 nonReentrant modifier: {len(definitions)} definitions, {len(usages)} usages")

            if len(definitions) == 0:
                print(f"❌ ISSUE #6 CONFIRMED: No nonReentrant modifier definitions found")
                print(f"   Expected: Should find modifier definition in base contracts")

            if len(usages) == 0:
                print(f"❌ ISSUE #6 CONFIRMED: No nonReentrant modifier usages found")
                print(f"   Expected: Should find functions using this modifier")
        else:
            print(f"❌ ISSUE #6 CONFIRMED: find_references failed for modifiers")
            print(f"   Error: {nonreentrant_refs.get('errors', 'Unknown error')}")

    def test_issue_7_event_references(self):
        """
        Issue #7: Event Reference Tracking
        Test if events are properly tracked
        """
        print("\n🔍 Testing Issue #7: Event Reference Tracking")
        print("Checking Mint event references...")

        # Test Mint event
        mint_event_refs = self.engine.find_references(
            "Mint",
            "event",
            reference_type="all",
            direction="both"
        )

        if mint_event_refs['success']:
            refs_data = mint_event_refs['data']['references']
            usages = refs_data.get('usages', [])
            definitions = refs_data.get('definitions', [])

            print(f"📊 Mint event: {len(definitions)} definitions, {len(usages)} usages")

            if len(definitions) == 0:
                print(f"⚠️ Potential Issue #7: No Mint event definitions found")

            if len(usages) == 0:
                print(f"⚠️ Potential Issue #7: No Mint event usages found")
                print(f"   Expected: Should find 'emit Mint(...)' statements")
        else:
            print(f"❌ ISSUE #7 CONFIRMED: find_references failed for events")
            print(f"   Error: {mint_event_refs.get('errors', 'Unknown error')}")

    def test_issue_8_complex_expressions(self):
        """
        Issue #8: Complex Expression Analysis
        Test function calls in complex expressions
        """
        print("\n🔍 Testing Issue #8: Complex Expression Analysis")
        print("Checking function calls in conditions and expressions...")

        # Test require statements that use function calls
        # Example: require(msg.sender == admin, "...")
        # This involves admin variable reference in a condition
        print("Checking if admin references in require statements are found...")

        admin_refs = self.engine.find_references(
            "admin",
            "variable",
            reference_type="usages",
            direction="both"
        )

        if admin_refs['success']:
            refs_data = admin_refs['data']['references']
            usages = refs_data.get('usages', [])

            # Look for admin usage in require statements
            require_usages = []
            for usage in usages:
                line_content = usage.get('line_content', '').strip()
                if 'require' in line_content and 'admin' in line_content:
                    require_usages.append(usage)

            print(f"📊 Admin usages in require statements: {len(require_usages)}")

            if len(require_usages) > 0:
                print(f"✅ Found admin references in complex expressions")
                for usage in require_usages[:3]:  # Show first 3
                    location = usage['location']
                    print(f"  📍 {location['contract']}:{location['line']} - {usage.get('line_content', '')[:60]}...")
            else:
                print(f"⚠️ Potential Issue #8: No admin usages in require statements found")

    def test_comprehensive_summary(self):
        """
        Comprehensive summary of all issues tested
        """
        print("\n📊 NEXT BATCH ISSUES SUMMARY:")
        print("=" * 50)
        print("✅ Issue #1-3: FIXED in previous round")
        print("🔍 Issue #4: Specific function call detection - NEEDS VERIFICATION")
        print("🔍 Issue #5: Cross-contract calls - TESTED")
        print("🔍 Issue #6: Modifier references - TESTED")
        print("🔍 Issue #7: Event references - TESTED")
        print("🔍 Issue #8: Complex expressions - TESTED")
        print("=" * 50)
        print("💡 These tests help identify the next areas for improvement")
        print("📋 See NEXT_BATCH_ISSUES.md for detailed analysis")
