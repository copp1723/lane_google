#!/usr/bin/env python3
"""
Route Debugging Utility for Lane Google
Helps verify and debug the new routing system
"""

import os
import sys
from tabulate import tabulate

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set minimal environment if not set
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('APP_ENVIRONMENT', 'development')

from src.main import app
from src.routes import (
    list_all_routes, 
    validate_route_consistency,
    BLUEPRINT_REGISTRY,
    ENVIRONMENT_BLUEPRINTS
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print('=' * 60)


def analyze_routes():
    """Analyze all registered routes"""
    with app.app_context():
        routes = list_all_routes(app)
        
        # Group routes by blueprint
        blueprint_routes = {}
        api_routes = []
        static_routes = []
        
        for route in routes:
            if route['path'].startswith('/api/'):
                api_routes.append(route)
            elif route['path'].startswith('/static/'):
                static_routes.append(route)
            else:
                # Try to determine blueprint from endpoint
                endpoint_parts = route['endpoint'].split('.')
                if len(endpoint_parts) > 1:
                    blueprint_name = endpoint_parts[0]
                    if blueprint_name not in blueprint_routes:
                        blueprint_routes[blueprint_name] = []
                    blueprint_routes[blueprint_name].append(route)
                else:
                    if 'misc' not in blueprint_routes:
                        blueprint_routes['misc'] = []
                    blueprint_routes['misc'].append(route)
        
        return {
            'all': routes,
            'by_blueprint': blueprint_routes,
            'api': api_routes,
            'static': static_routes
        }


def print_route_summary():
    """Print a summary of all routes"""
    route_analysis = analyze_routes()
    
    print_section("Route Summary")
    print(f"Total Routes: {len(route_analysis['all'])}")
    print(f"API Routes: {len(route_analysis['api'])}")
    print(f"Static Routes: {len(route_analysis['static'])}")
    print(f"Blueprints with Routes: {len(route_analysis['by_blueprint'])}")


def print_routes_by_blueprint():
    """Print routes grouped by blueprint"""
    route_analysis = analyze_routes()
    
    print_section("Routes by Blueprint")
    
    for blueprint_name, routes in sorted(route_analysis['by_blueprint'].items()):
        print(f"\n{blueprint_name} ({len(routes)} routes):")
        
        # Prepare table data
        table_data = []
        for route in sorted(routes, key=lambda r: r['path']):
            table_data.append([
                route['path'],
                route['methods'],
                route['endpoint']
            ])
        
        print(tabulate(
            table_data,
            headers=['Path', 'Methods', 'Endpoint'],
            tablefmt='grid'
        ))


def print_api_routes():
    """Print all API routes"""
    route_analysis = analyze_routes()
    
    print_section("API Routes")
    
    # Group by prefix
    prefixes = {}
    for route in route_analysis['api']:
        # Extract prefix (e.g., /api/v1/campaigns -> /api/v1/campaigns)
        parts = route['path'].split('/')
        if len(parts) >= 4:
            prefix = '/'.join(parts[:4])
        else:
            prefix = route['path']
        
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append(route)
    
    # Print grouped routes
    for prefix, routes in sorted(prefixes.items()):
        print(f"\n{prefix}/* ({len(routes)} routes):")
        
        table_data = []
        for route in sorted(routes, key=lambda r: r['path']):
            # Show relative path
            rel_path = route['path'][len(prefix):] or '/'
            table_data.append([
                rel_path,
                route['methods'],
                route['endpoint'].split('.')[-1]  # Just the function name
            ])
        
        print(tabulate(
            table_data,
            headers=['Path', 'Methods', 'Handler'],
            tablefmt='simple'
        ))


def check_route_conflicts():
    """Check for route conflicts and issues"""
    print_section("Route Validation")
    
    with app.app_context():
        issues = validate_route_consistency(app)
        
        if not any(issues.values()):
            print("✓ No route conflicts detected!")
        else:
            for issue_type, issue_list in issues.items():
                if issue_list:
                    print(f"\n⚠ {issue_type.replace('_', ' ').title()}:")
                    for issue in issue_list:
                        print(f"  - {issue}")


def check_blueprint_registration():
    """Check blueprint registration status"""
    print_section("Blueprint Registration Status")
    
    from src.config.settings import settings
    from src.routes import get_enabled_blueprints
    
    enabled = get_enabled_blueprints(settings.environment)
    
    print(f"Environment: {settings.environment}")
    print(f"Enabled Blueprints: {len(enabled)}")
    
    # Check each blueprint
    table_data = []
    for bp_name, bp_config in sorted(BLUEPRINT_REGISTRY.items()):
        enabled_in_env = bp_name in enabled
        explicitly_disabled = not bp_config.get('enabled', True)
        
        status = "✓ Enabled" if enabled_in_env else "✗ Disabled"
        if explicitly_disabled:
            status = "⚠ Explicitly Disabled"
        
        table_data.append([
            bp_name,
            bp_config['module'].split('.')[-1],
            bp_config.get('url_prefix', '/'),
            status
        ])
    
    print(tabulate(
        table_data,
        headers=['Blueprint', 'Module', 'Prefix', 'Status'],
        tablefmt='grid'
    ))


def check_frontend_compatibility():
    """Check if API routes match frontend expectations"""
    print_section("Frontend Compatibility Check")
    
    # Expected routes from frontend config
    expected_routes = [
        ('/api/v1/auth/login', 'POST'),
        ('/api/v1/auth/register', 'POST'),
        ('/api/v1/ai/chat', 'POST'),
        ('/api/v1/ai/stream', 'POST'),
        ('/api/v1/campaigns', 'GET'),
        ('/api/v1/keywords/research', 'POST'),
        ('/api/v1/keyword-analytics/comprehensive-analysis', 'POST'),
        ('/api/v1/campaign-analytics/performance-analysis', 'GET'),
        ('/api/analytics/dashboard/<customer_id>', 'GET'),  # Legacy
        ('/api/budget-pacing/summary/<customer_id>', 'GET'),  # Legacy
        ('/api/performance/summary/<customer_id>', 'GET'),  # Legacy
    ]
    
    route_analysis = analyze_routes()
    registered_paths = {r['path']: r['methods'] for r in route_analysis['all']}
    
    print("\nChecking expected frontend routes:")
    all_good = True
    
    for expected_path, expected_method in expected_routes:
        # Handle parameterized routes
        found = False
        for reg_path, methods in registered_paths.items():
            if '<' in expected_path:
                # Check pattern match
                pattern = expected_path.replace('<customer_id>', '<[^>]+>')
                pattern = pattern.replace('<campaign_id>', '<[^>]+>')
                import re
                if re.match(pattern.replace('/', '\\/'), reg_path):
                    if expected_method in methods:
                        found = True
                        break
            else:
                if reg_path == expected_path and expected_method in methods:
                    found = True
                    break
        
        if found:
            print(f"  ✓ {expected_method} {expected_path}")
        else:
            print(f"  ✗ {expected_method} {expected_path} - NOT FOUND")
            all_good = False
    
    if all_good:
        print("\n✓ All frontend routes are available!")
    else:
        print("\n⚠ Some frontend routes are missing!")


def print_environment_comparison():
    """Compare blueprint availability across environments"""
    print_section("Environment Blueprint Comparison")
    
    environments = ['development', 'production', 'testing']
    
    # Build comparison table
    table_data = []
    all_blueprints = set()
    for env_bps in ENVIRONMENT_BLUEPRINTS.values():
        all_blueprints.update(env_bps)
    
    for bp_name in sorted(all_blueprints):
        row = [bp_name]
        for env in environments:
            if bp_name in ENVIRONMENT_BLUEPRINTS.get(env, []):
                row.append('✓')
            else:
                row.append('✗')
        table_data.append(row)
    
    print(tabulate(
        table_data,
        headers=['Blueprint'] + [env.capitalize() for env in environments],
        tablefmt='grid'
    ))


def main():
    """Main debug function"""
    print("Lane Google Route Debugging Utility")
    print("=" * 60)
    
    # Run all checks
    print_route_summary()
    check_blueprint_registration()
    check_route_conflicts()
    check_frontend_compatibility()
    print_environment_comparison()
    
    # Detailed route listings
    response = input("\nShow detailed route listings? (y/n): ").lower()
    if response == 'y':
        print_routes_by_blueprint()
        print_api_routes()
    
    # Export option
    response = input("\nExport routes to file? (y/n): ").lower()
    if response == 'y':
        with open('routes_debug_output.txt', 'w') as f:
            # Redirect print to file
            import contextlib
            with contextlib.redirect_stdout(f):
                print_route_summary()
                print_routes_by_blueprint()
                print_api_routes()
        print("Routes exported to routes_debug_output.txt")


if __name__ == '__main__':
    main()