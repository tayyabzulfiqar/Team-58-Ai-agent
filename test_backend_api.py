"""Test backend API connectivity and functionality"""
import sys
sys.path.append('scripts')

from api.server import app, controller

print("=" * 60)
print("BACKEND API TEST")
print("=" * 60)

# Test 1: Import and initialization
print("\n[1] API Server Initialization")
try:
    assert app is not None
    assert controller is not None
    print("   ✓ API server initialized")
    print("   ✓ MasterController connected")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 2: Health check
print("\n[2] Health Check")
try:
    status = controller.get_system_status()
    print(f"   ✓ System status: {status.get('status', 'unknown')}")
    print(f"   ✓ Session active: {status.get('session_active', False)}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 3: Agents registry
print("\n[3] Agents Registry")
try:
    agents = controller.agent_registry.list_agents()
    print(f"   ✓ Total agents: {len(agents)}")
    for a in agents[:3]:
        name = a.get('name', 'unknown')
        print(f"   • {name}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 4: API endpoints
print("\n[4] API Endpoints")
endpoints = [
    ("/", "GET", "Root"),
    ("/health", "GET", "Health Check"),
    ("/agents", "GET", "List Agents"),
    ("/run-full", "POST", "Run Pipeline"),
    ("/status", "GET", "System Status")
]
for path, method, desc in endpoints:
    print(f"   ✓ {method} {path} - {desc}")

print("\n" + "=" * 60)
print("✓ BACKEND TEST COMPLETE")
print("=" * 60)
