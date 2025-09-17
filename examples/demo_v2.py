#!/usr/bin/env python3
"""
Sol-Query V2 API Demo
===================

Comprehensive demonstration of the SolidityQueryEngineV2 capabilities.
This demo showcases all three core methods with real-world security analysis examples.

Usage:
    python demo_v2.py

Features Demonstrated:
- Universal query_code() method with advanced filtering
- Multi-depth get_details() analysis
- Reference tracking with find_references()
- Security pattern detection
- Performance optimization techniques
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

# Import the V2 engine
from sol_query.query.engine_v2 import SolidityQueryEngineV2

def print_banner(title: str):
    """Print a formatted banner for demo sections."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def print_result_summary(result: Dict[str, Any], show_data: bool = True):
    """Print a formatted summary of query results."""
    if result['success']:
        print(f"✅ Success: {result['query_info']['result_count']} results in {result['query_info']['execution_time']:.3f}s")

        if show_data and 'data' in result:
            if 'results' in result['data']:
                # query_code results
                results = result['data']['results']
                if results:
                    print("📊 Results:")
                    for i, item in enumerate(results[:3]):  # Show first 3
                        location = item.get('location', {})
                        print(f"  {i+1}. {item.get('name', 'unnamed')} ({item.get('type', 'unknown')})")
                        if location.get('contract'):
                            print(f"     Contract: {location['contract']}")
                    if len(results) > 3:
                        print(f"     ... and {len(results) - 3} more")

            elif 'elements' in result['data']:
                # get_details results
                elements = result['data']['elements']
                print("📊 Analysis Results:")
                for name, analysis in elements.items():
                    if analysis.get('found'):
                        print(f"  ✅ {name}: Successfully analyzed")
                        if 'comprehensive_info' in analysis:
                            security = analysis['comprehensive_info'].get('security_analysis', {})
                            if security.get('issues'):
                                print(f"     ⚠️  {len(security['issues'])} security issues found")
                    else:
                        print(f"  ❌ {name}: {analysis.get('error', 'Not found')}")

            elif 'references' in result['data']:
                # find_references results
                refs = result['data']['references']
                print("📊 Reference Analysis:")
                print(f"  📍 Usages: {len(refs.get('usages', []))}")
                print(f"  📝 Definitions: {len(refs.get('definitions', []))}")
                if refs.get('call_chains'):
                    print(f"  🔗 Call chains: {len(refs['call_chains'])}")

        # Show warnings and suggestions
        if result.get('warnings'):
            for warning in result['warnings']:
                print(f"⚠️  Warning: {warning}")

        if result.get('suggestions'):
            print("💡 Suggestions:")
            for suggestion in result['suggestions'][:2]:  # Show first 2 suggestions
                print(f"   • {suggestion}")
    else:
        print(f"❌ Failed: {', '.join(result.get('errors', ['Unknown error']))}")

def demo_basic_queries(engine: SolidityQueryEngineV2):
    """Demo basic query_code functionality."""
    print_banner("1. Basic Query Operations")

    # Find all functions
    print_section("Finding All Functions")
    result = engine.query_code("functions")
    print_result_summary(result, show_data=False)
    print(f"📊 Found {result['data']['summary']['total_count']} total functions")

    # Find external functions
    print_section("Finding External Functions")
    result = engine.query_code("functions", {
        "visibility": ["external", "public"]  # Use list to catch both
    })
    print_result_summary(result)

    # Alternative: Check what visibility values we actually have
    if not result['data']['results']:
        print("🔍 Debugging: Let's check actual visibility values...")
        all_functions = engine.query_code("functions")
        if all_functions['success'] and all_functions['data']['results']:
            sample_func = all_functions['data']['results'][0]
            print(f"   Sample function visibility: {sample_func.get('visibility', 'unknown')}")
            print("   Trying with the actual visibility format...")

            # Try a broader search to show we have functions
            result = engine.query_code("functions", {
                "names": ["transfer*", "approve*", "balance*"]
            })
            print_result_summary(result)

    # Find contracts with pattern matching
    print_section("Finding Token Contracts")
    result = engine.query_code("contracts", {
        "names": ["*Token*", "*ERC*", "Token"]  # Add exact match
    })
    print_result_summary(result)

    # If no results, show what contracts we actually have
    if not result['data']['results']:
        print("🔍 Let's see what contracts are available...")
        all_contracts = engine.query_code("contracts")
        if all_contracts['success']:
            print("📋 Available contracts:")
            for contract in all_contracts['data']['results'][:5]:
                print(f"   • {contract['name']}")

            # Try finding any contract
            if all_contracts['data']['results']:
                first_contract = all_contracts['data']['results'][0]['name']
                result = engine.query_code("contracts", {
                    "names": [first_contract]
                })
                print_result_summary(result)

    # Find state variables
    print_section("Finding State Variables")
    result = engine.query_code("variables")  # Start with all variables
    print_result_summary(result)

    if result['success'] and result['data']['results']:
        print("📋 Sample variables found:")
        for var in result['data']['results'][:3]:
            print(f"   • {var['name']} ({var.get('type_name', 'unknown type')})")

        # Now try with state variable filter
        state_vars = engine.query_code("variables", {
            "is_state_variable": True
        })
        if state_vars['success']:
            print(f"   State variables: {state_vars['data']['summary']['total_count']}")
    else:
        print("🔍 No variables found, checking if we have any AST nodes...")
        # Try a very broad search
        all_elements = engine.query_code("functions")
        if all_elements['success']:
            print(f"   Found {all_elements['data']['summary']['total_count']} functions, so parsing is working")

def demo_advanced_filtering(engine: SolidityQueryEngineV2):
    """Demo advanced filtering capabilities."""
    print_banner("2. Advanced Filtering & Security Analysis")

    # Find functions with external calls
    print_section("Functions with External Calls")
    result = engine.query_code("functions", {
        "has_external_calls": True
    })
    print_result_summary(result)

    # Find payable functions that change state
    print_section("Payable Functions Changing State")
    result = engine.query_code("functions", {
        "is_payable": True,
        "changes_state": True
    })
    print_result_summary(result)

    # Find functions with specific modifiers
    print_section("Functions with Access Control")
    result = engine.query_code("functions", {
        "modifiers": ["onlyOwner", "validAddress"]
    })
    print_result_summary(result)

    # Complex filtering with scope
    print_section("Complex Query with Scope")
    result = engine.query_code("functions", {
        "visibility": ["public", "external"],
        "names": ["transfer*", "*withdraw*"]
    }, scope={
        "contracts": ["Token"]
    }, include=["source", "calls", "modifiers"])
    print_result_summary(result)

    if result['success'] and result['data']['results']:
        # Show detailed information for first result
        func = result['data']['results'][0]
        print(f"📝 Detailed info for {func['name']}:")
        if func.get('modifiers'):
            print(f"   Modifiers: {func['modifiers']}")
        if func.get('calls'):
            print(f"   Makes {len(func['calls'])} calls")

def demo_security_patterns(engine: SolidityQueryEngineV2):
    """Demo security analysis patterns."""
    print_banner("3. Security Pattern Detection")

    # Reentrancy vulnerability detection
    print_section("Potential Reentrancy Vulnerabilities")
    result = engine.query_code("functions", {
        "has_external_calls": True,
        "changes_state": True,
        "visibility": ["public", "external"]
    }, include=["source", "calls"])
    print_result_summary(result)

    if result['success'] and result['data']['results']:
        print("🔍 Reentrancy Analysis:")
        for func in result['data']['results'][:2]:
            print(f"  ⚠️  {func['location']['contract']}.{func['name']}")
            if func.get('calls'):
                ext_calls = [c for c in func['calls'] if c.get('type') == 'external']
                print(f"     External calls: {len(ext_calls)}")

    # Missing access control
    print_section("Functions Without Access Control")
    result = engine.query_code("functions", {
        "visibility": ["public", "external"],
        "modifiers": []  # No modifiers
    })
    print_result_summary(result)

    # Asset transfer functions
    print_section("Asset Transfer Functions")
    result = engine.query_code("functions", {
        "has_asset_transfers": True
    })
    print_result_summary(result)

def demo_detailed_analysis(engine: SolidityQueryEngineV2):
    """Demo get_details functionality."""
    print_banner("4. Detailed Element Analysis")

    # Basic analysis of transfer functions
    print_section("Basic Function Analysis")
    result = engine.get_details("function", ["transfer", "transferFrom"])
    print_result_summary(result)

    # Detailed analysis of a contract
    print_section("Detailed Contract Analysis")
    result = engine.get_details("contract", ["Token"],
                               options={"include_source": True, "resolve_inheritance": True})
    print_result_summary(result)

    if result['success']:
        token_analysis = result['data']['elements'].get('Token')
        if token_analysis and token_analysis['found']:
            detailed = token_analysis.get('detailed_info', {})
            print(f"📊 Token contract details:")
            if detailed.get('functions'):
                print(f"   Functions: {len(detailed['functions'])}")
            if detailed.get('variables'):
                print(f"   Variables: {len(detailed['variables'])}")

    # Comprehensive security analysis
    print_section("Comprehensive Security Analysis")
    result = engine.get_details("function", ["transfer"],
                               options={"show_call_chains": True, "include_source": True})
    print_result_summary(result)

    if result['success']:
        transfer_analysis = result['data']['elements'].get('transfer')
        if transfer_analysis and transfer_analysis['found']:
            comprehensive = transfer_analysis.get('comprehensive_info', {})
            security = comprehensive.get('security_analysis', {})

            print(f"🛡️  Security Analysis for transfer():")
            print(f"   Risk level: {security.get('risk_level', 'unknown')}")
            print(f"   Issues found: {len(security.get('issues', []))}")

            for issue in security.get('issues', []):
                print(f"     • {issue.get('type', 'unknown')}: {issue.get('severity', 'unknown')}")

            recommendations = security.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations: {', '.join(recommendations[:2])}")

def demo_reference_analysis(engine: SolidityQueryEngineV2):
    """Demo find_references functionality."""
    print_banner("5. Reference & Relationship Analysis")

    # Find usages of totalSupply
    print_section("totalSupply Variable References")
    result = engine.find_references("totalSupply", "variable",
                                   reference_type="all",
                                   direction="both")
    print_result_summary(result)

    # Find transfer function references
    print_section("Transfer Function References")
    result = engine.find_references("transfer", "function",
                                   reference_type="usages",
                                   filters={"contracts": ["Token"]})
    print_result_summary(result)

    if result['success']:
        usages = result['data']['references']['usages']
        if usages:
            print("📍 Usage locations:")
            for usage in usages[:3]:
                loc = usage.get('location', {})
                print(f"   • {usage.get('usage_type', 'unknown')} in {loc.get('contract', 'unknown')}")
                if usage.get('context'):
                    context = usage['context'].replace('\n', ' ')[:60]
                    print(f"     Context: {context}...")

    # Call chain analysis
    print_section("Call Chain Analysis")
    result = engine.find_references("transfer", "function",
                                   direction="both",
                                   max_depth=2,
                                   options={"show_call_chains": True})
    print_result_summary(result)

    if result['success']:
        chains = result['data']['references'].get('call_chains', [])
        if chains:
            print("🔗 Call chains found:")
            for i, chain in enumerate(chains[:3]):
                print(f"   {i+1}. {' -> '.join(chain)}")

def demo_performance_optimization(engine: SolidityQueryEngineV2):
    """Demo performance optimization techniques."""
    print_banner("6. Performance Optimization Techniques")

    # Scoped query for better performance
    print_section("Scoped Query (Better Performance)")
    start_time = time.time()
    result = engine.query_code("functions", {
        "visibility": "external"
    }, scope={
        "contracts": ["Token"]
    }, options={
        "max_results": 10
    })
    scoped_time = time.time() - start_time
    print_result_summary(result, show_data=False)
    print(f"⚡ Scoped query: {scoped_time:.3f}s")

    # Broad query for comparison
    print_section("Broad Query (For Comparison)")
    start_time = time.time()
    result_broad = engine.query_code("functions", {
        "visibility": "external"
    })
    broad_time = time.time() - start_time
    print_result_summary(result_broad, show_data=False)
    print(f"🐌 Broad query: {broad_time:.3f}s")

    if scoped_time < broad_time:
        speedup = broad_time / scoped_time
        print(f"🚀 Scoped query is {speedup:.1f}x faster!")

    # Different options comparison
    print_section("Analysis Options Comparison")

    option_sets = [
        ("minimal", {}),
        ("with_source", {"include_source": True}),
        ("comprehensive", {"include_source": True, "show_call_chains": True, "resolve_inheritance": True})
    ]
    times = {}

    for name, options in option_sets:
        start_time = time.time()
        result = engine.get_details("function", ["transfer"], options=options)
        times[name] = time.time() - start_time
        print(f"📊 {name.capitalize()} analysis: {times[name]:.3f}s")

    print("\n💡 Performance Tips:")
    print("   • Use specific contract scopes when possible")
    print("   • Choose appropriate analysis options")
    print("   • Limit results with max_results option")
    print("   • Use filters early to reduce search space")

def demo_real_world_security_analysis(engine: SolidityQueryEngineV2):
    """Demo comprehensive real-world security analysis workflow."""
    print_banner("7. Real-World Security Analysis Workflow")

    print_section("Step 1: Identify High-Risk Functions")

    # First, let's see what functions we have
    all_functions = engine.query_code("functions")
    if all_functions['success']:
        total_functions = all_functions['data']['summary']['total_count']
        print(f"📊 Total functions available for analysis: {total_functions}")

        # Get sample function names for analysis
        sample_functions = [f['name'] for f in all_functions['data']['results'][:5]]
        print(f"🔍 Analyzing sample functions: {', '.join(sample_functions)}")

        # For demo purposes, let's analyze these functions
        func_names = sample_functions

        if func_names:
            print_section("Step 2: Detailed Security Analysis")
            # Analyze each function in detail
            security_analysis = engine.get_details("function", func_names[:3],
                                                 options={"show_call_chains": True, "include_source": True})

            high_risk_functions = []
            if security_analysis['success']:
                for func_name, analysis in security_analysis['data']['elements'].items():
                    if analysis.get('found'):
                        security = analysis.get('comprehensive_info', {}).get('security_analysis', {})
                        if security.get('risk_level') == 'high':
                            high_risk_functions.append(func_name)
                            print(f"🚨 HIGH RISK: {func_name}")
                            for issue in security.get('issues', []):
                                print(f"   • {issue.get('description', 'Unknown issue')}")

            print_section("Step 3: Cross-Reference Analysis")
            # For each high-risk function, find what calls it
            for func_name in high_risk_functions[:2]:  # Analyze first 2
                refs = engine.find_references(func_name, "function",
                                            reference_type="usages")
                if refs['success']:
                    usages = refs['data']['references']['usages']
                    print(f"📞 {func_name} is called by {len(usages)} locations")
                    if len(usages) > 3:
                        print(f"   ⚠️  Widely used high-risk function!")

            print_section("Step 4: Generate Security Report")
            security_report = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_functions_analyzed': len(func_names),
                'high_risk_functions': len(high_risk_functions),
                'risk_functions': high_risk_functions,
                'recommendations': [
                    'Review high-risk functions for reentrancy vulnerabilities',
                    'Consider adding access controls to widely-used functions',
                    'Implement proper error handling for external calls'
                ]
            }

            print("📋 Security Report Generated:")
            print(json.dumps(security_report, indent=2))

def demo_export_analysis(engine: SolidityQueryEngineV2):
    """Demo exporting analysis results for external tools."""
    print_banner("8. Export Analysis for External Tools")

    print_section("Comprehensive Data Export")

    # Get all functions with full details (since filtering might not work as expected)
    result = engine.query_code("functions", {}, include=["source", "calls", "variables", "modifiers"])

    # If we have no results, try without any filters
    if not result['success'] or not result['data']['results']:
        print("🔍 Trying basic function query for export...")
        result = engine.query_code("functions")

    if result['success']:
        export_data = {
            'analysis_metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'engine_version': 'V2',
                'total_functions': len(result['data']['results'])
            },
            'functions': []
        }

        # Process each function for export
        for func in result['data']['results']:
            # Safely access location data
            location = func.get('location', {})
            contract_name = location.get('contract') if location else None

            # Count external calls if they exist
            calls = func.get('calls', [])
            external_calls = len([c for c in calls if c.get('type') == 'external']) if isinstance(calls, list) else 0

            # Get variables if they exist
            variables = func.get('variables', [])
            variables_list = variables if isinstance(variables, list) else []

            func_data = {
                'name': func.get('name', 'unknown'),
                'contract': contract_name,
                'visibility': func.get('visibility', 'unknown'),
                'signature': func.get('signature'),
                'external_calls': external_calls,
                'variables_accessed': variables_list,
                'modifiers': func.get('modifiers', []),
                'has_source': bool(func.get('source_code'))
            }
            export_data['functions'].append(func_data)

        # Save to file
        export_file = Path("security_analysis_export.json")
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"💾 Exported analysis to {export_file}")
        print(f"📊 Export contains {len(export_data['functions'])} function analyses")

        # Show summary statistics
        total_calls = sum(f['external_calls'] for f in export_data['functions'])
        functions_with_modifiers = len([f for f in export_data['functions'] if f['modifiers']])
        total_variables = sum(len(f['variables_accessed']) for f in export_data['functions'])

        print(f"📈 Analysis Summary:")
        print(f"   • Total external calls: {total_calls}")
        print(f"   • Functions with modifiers: {functions_with_modifiers}")
        print(f"   • Total variables accessed: {total_variables}")
        print(f"   • Coverage: {len(export_data['functions'])} functions analyzed")

def main():
    """Main demo function."""
    print("🎯 Sol-Query V2 API Comprehensive Demo")
    print("====================================")
    print()
    print("This demo showcases the powerful V2 API with real Solidity contracts.")
    print("The V2 engine provides 3 core methods for any analysis need:")
    print("  • query_code() - Universal query function")
    print("  • get_details() - Multi-depth element analysis")
    print("  • find_references() - Reference tracking & call graphs")
    print()

    # Initialize engine with sample contracts
    print("🚀 Initializing SolidityQueryEngineV2...")

    # Use the fixtures directory for comprehensive examples
    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    sample_contract = fixtures_dir / "sample_contract.sol"

    if not sample_contract.exists():
        print(f"❌ Sample contract not found at: {sample_contract}")
        print("Please ensure you're running this demo from the project root directory.")
        return

    try:
        # Load the engine with sample contracts
        engine = SolidityQueryEngineV2()
        engine.load_sources([
            sample_contract,
            fixtures_dir / "detailed_scenarios" / "RETHInteractions.sol",
            fixtures_dir / "composition_and_imports"
        ])

        print("✅ Engine initialized successfully!")

        # Get basic statistics
        stats_result = engine.query_code("contracts")
        if stats_result['success']:
            total_contracts = stats_result['data']['summary']['total_count']
            print(f"📊 Loaded {total_contracts} contracts for analysis")

        # Run all demo sections
        demo_basic_queries(engine)
        demo_advanced_filtering(engine)
        demo_security_patterns(engine)
        demo_detailed_analysis(engine)
        demo_reference_analysis(engine)
        demo_performance_optimization(engine)
        demo_real_world_security_analysis(engine)
        demo_export_analysis(engine)

        # Final summary
        print_banner("Demo Complete! 🎉")
        print()
        print("✅ All V2 API features demonstrated successfully!")
        print()
        print("🔍 What you learned:")
        print("  • query_code() handles any Solidity construct with advanced filters")
        print("  • get_details() provides basic/detailed/comprehensive analysis")
        print("  • find_references() tracks relationships and call chains")
        print("  • Built-in security pattern detection")
        print("  • Performance optimization techniques")
        print("  • Real-world security analysis workflows")
        print()
        print("📚 Next steps:")
        print("  • Read the full V2 API documentation: docs/api-reference-v2.md")
        print("  • Try the V2 API with your own contracts")
        print("  • Explore advanced filtering combinations")
        print("  • Build custom security analysis tools")
        print()
        print("🚀 Happy analyzing!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure sol-query is properly installed:")
        print("  pip install -e .")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Please check that all required files exist and the engine is properly set up.")

if __name__ == "__main__":
    main()