#!/usr/bin/env python3
"""
🧪 Jamie AI DevOps Copilot - Sprint 4 Test Suite
Chat Portal Interface - Comprehensive Validation

Tests all components of the ChatGPT-like web interface:
- Portal file structure and configuration
- Next.js, TypeScript, and Tailwind setup
- React components and API integration
- WebSocket support and real-time features
"""

import os
import json
import sys
from pathlib import Path

def test_portal_structure():
    """Test that the portal directory structure is correct"""
    print("🧪 Testing portal file structure...")
    
    base_path = Path("portal")
    required_files = [
        "package.json",
        "next.config.js", 
        "tailwind.config.js",
        "tsconfig.json",
        "postcss.config.js",
        "app/layout.tsx",
        "app/page.tsx",
        "app/globals.css",
        "components/chat/ChatInterface.tsx",
        "components/chat/ChatMessage.tsx",
        "components/chat/ChatInput.tsx",
        "components/layout/Header.tsx",
        "components/layout/Sidebar.tsx",
        "lib/jamie-api.ts",
        "lib/utils.ts",
        "types/chat.ts",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required portal files exist")
    return True

def test_package_json():
    """Test package.json configuration"""
    print("🧪 Testing package.json configuration...")
    
    package_path = Path("portal/package.json")
    if not package_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_path) as f:
        package_data = json.load(f)
    
    # Check required dependencies
    required_deps = [
        "next", "react", "react-dom", "typescript",
        "tailwindcss", "lucide-react", "react-markdown",
        "highlight.js", "clsx", "date-fns"
    ]
    
    dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
    
    missing_deps = []
    for dep in required_deps:
        if dep not in dependencies:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        return False
    
    # Check scripts
    required_scripts = ["dev", "build", "start", "lint"]
    scripts = package_data.get("scripts", {})
    
    missing_scripts = []
    for script in required_scripts:
        if script not in scripts:
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Missing scripts: {missing_scripts}")
        return False
    
    print("✅ Package.json configuration is correct")
    return True

def test_typescript_config():
    """Test TypeScript configuration"""
    print("🧪 Testing TypeScript configuration...")
    
    tsconfig_path = Path("portal/tsconfig.json")
    if not tsconfig_path.exists():
        print("❌ tsconfig.json not found")
        return False
    
    with open(tsconfig_path) as f:
        tsconfig_data = json.load(f)
    
    # Check important compiler options
    compiler_options = tsconfig_data.get("compilerOptions", {})
    
    required_options = {
        "strict": True,
        "jsx": "preserve",
        "module": "esnext",
        "moduleResolution": "bundler"
    }
    
    for option, expected_value in required_options.items():
        if compiler_options.get(option) != expected_value:
            print(f"❌ TypeScript option {option} should be {expected_value}")
            return False
    
    # Check path mappings
    paths = compiler_options.get("paths", {})
    if "@/*" not in paths:
        print("❌ Missing path mapping for @/*")
        return False
    
    print("✅ TypeScript configuration is correct")
    return True

def test_tailwind_config():
    """Test Tailwind CSS configuration"""
    print("🧪 Testing Tailwind configuration...")
    
    tailwind_path = Path("portal/tailwind.config.js")
    if not tailwind_path.exists():
        print("❌ tailwind.config.js not found")
        return False
    
    # Read the file content
    with open(tailwind_path) as f:
        content = f.read()
    
    # Check for Jamie theme colors
    jamie_colors = ["jamie", "primary", "secondary", "success", "warning", "error"]
    for color in jamie_colors:
        if color not in content:
            print(f"❌ Missing Jamie color: {color}")
            return False
    
    # Check for custom animations
    animations = ["fade-in", "slide-up", "pulse-glow", "typing"]
    for animation in animations:
        if animation not in content:
            print(f"❌ Missing animation: {animation}")
            return False
    
    print("✅ Tailwind configuration includes Jamie theme")
    return True

def test_react_components():
    """Test React component structure"""
    print("🧪 Testing React components...")
    
    components = [
        "portal/components/chat/ChatInterface.tsx",
        "portal/components/chat/ChatMessage.tsx", 
        "portal/components/chat/ChatInput.tsx",
        "portal/components/layout/Header.tsx",
        "portal/components/layout/Sidebar.tsx"
    ]
    
    for component_path in components:
        path = Path(component_path)
        if not path.exists():
            print(f"❌ Component not found: {component_path}")
            return False
        
        with open(path) as f:
            content = f.read()
        
        # Check for React imports
        if "'use client';" not in content and "import React" not in content:
            print(f"❌ Component {component_path} missing React imports")
            return False
        
        # Check for TypeScript
        if "interface" not in content and "type" not in content:
            print(f"❌ Component {component_path} should use TypeScript interfaces")
            return False
    
    print("✅ All React components are properly structured")
    return True

def test_api_integration():
    """Test API integration files"""
    print("🧪 Testing API integration...")
    
    # Test jamie-api.ts
    api_path = Path("portal/lib/jamie-api.ts")
    if not api_path.exists():
        print("❌ jamie-api.ts not found")
        return False
    
    with open(api_path) as f:
        api_content = f.read()
    
    # Check for required API methods
    api_methods = ["healthCheck", "sendMessage", "getClusterStatus", "createWebSocket"]
    for method in api_methods:
        if method not in api_content:
            print(f"❌ Missing API method: {method}")
            return False
    
    # Test types file
    types_path = Path("portal/types/chat.ts")
    if not types_path.exists():
        print("❌ chat.ts types not found")
        return False
    
    with open(types_path) as f:
        types_content = f.read()
    
    # Check for required interfaces
    interfaces = ["ChatMessage", "ChatSession", "JamieResponse", "JamieHealthStatus"]
    for interface in interfaces:
        if f"interface {interface}" not in types_content:
            print(f"❌ Missing interface: {interface}")
            return False
    
    print("✅ API integration is properly implemented")
    return True

def test_websocket_support():
    """Test WebSocket support in API client"""
    print("🧪 Testing WebSocket support...")
    
    api_path = Path("portal/lib/jamie-api.ts")
    with open(api_path) as f:
        content = f.read()
    
    # Check for WebSocket implementation
    websocket_features = ["createWebSocket", "WebSocket", "ws://", "wss://"]
    for feature in websocket_features:
        if feature not in content:
            print(f"❌ Missing WebSocket feature: {feature}")
            return False
    
    print("✅ WebSocket support is implemented")
    return True

def test_next_config():
    """Test Next.js configuration"""
    print("🧪 Testing Next.js configuration...")
    
    config_path = Path("portal/next.config.js")
    if not config_path.exists():
        print("❌ next.config.js not found")
        return False
    
    with open(config_path) as f:
        content = f.read()
    
    # Check for API rewrites
    if "rewrites" not in content:
        print("❌ Missing API rewrites configuration")
        return False
    
    # Check for environment variables
    if "JAMIE_API_URL" not in content:
        print("❌ Missing Jamie API URL configuration")
        return False
    
    print("✅ Next.js configuration is correct")
    return True

def test_documentation():
    """Test documentation completeness"""
    print("🧪 Testing documentation...")
    
    readme_path = Path("portal/README.md")
    if not readme_path.exists():
        print("❌ Portal README.md not found")
        return False
    
    with open(readme_path) as f:
        readme_content = f.read()
    
    # Check for required sections
    required_sections = [
        "Features", "Tech Stack", "Installation", 
        "Usage", "Development", "Deployment"
    ]
    
    for section in required_sections:
        if section not in readme_content:
            print(f"❌ Missing documentation section: {section}")
            return False
    
    print("✅ Documentation is complete")
    return True

def run_all_tests():
    """Run all Sprint 4 tests"""
    print("🚀 Starting Jamie Sprint 4 Chat Portal Tests")
    print("=" * 60)
    
    tests = [
        ("Portal Structure", test_portal_structure),
        ("Package Configuration", test_package_json),
        ("TypeScript Setup", test_typescript_config),
        ("Tailwind Theme", test_tailwind_config),
        ("React Components", test_react_components),
        ("API Integration", test_api_integration),
        ("WebSocket Support", test_websocket_support),
        ("Next.js Config", test_next_config),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"🧪 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SPRINT 4 TESTS PASSED!")
        print("✨ Jamie's Chat Portal is ready for production!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        print("🔧 Please fix the issues before deployment")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 