#!/usr/bin/env python3
"""
🧪 Jamie AI DevOps Copilot - Sprint 5 Test Suite
Slack Integration - Comprehensive Validation

=== WHAT THIS FILE DOES ===
Quality assurance for Jamie's Slack integration! Tests everything works correctly:
- 📁 File Structure: All required files exist and are properly organized
- 🔧 Code Quality: Syntax is valid, imports work, functions exist
- 🧠 Logic Testing: Intent extraction, formatting, notifications work correctly
- 🇬🇧 Personality: British expressions and greetings are charming
- 📦 Dependencies: All required packages are installed and configured

=== TESTING PHILOSOPHY ===
1. Start Simple: Can we import files without errors?
2. Test Structure: Are all expected functions and classes present?
3. Test Logic: Do the smart functions actually work correctly?
4. Test Integration: Do components work together?
5. Test Production: Are we ready for real users?

=== FOR ADHD BRAINS ===
Think of this as Jamie's "health checkup" - we test everything systematically to make sure Jamie is ready to help teams without any surprises!

Each test is focused and clear - pass/fail, no ambiguity.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
import unittest
from unittest.mock import Mock, AsyncMock, patch

# ==========================================
# 🗂️ FILE STRUCTURE VALIDATION
# ==========================================

def test_slack_integration_structure():
    """
    🧪 Test that the Slack integration directory structure is correct
    
    🎯 PURPOSE: Ensure all required files exist before testing their contents
    
    WHAT WE CHECK:
    - slack/ directory exists
    - All 6 core files are present
    - No missing components that would break the integration
    
    WHY THIS MATTERS:
    - Missing files = runtime crashes
    - Correct structure = easier maintenance
    - Clear expectations for developers
    
    💡 ADHD TIP: File structure tests catch "obvious" problems early - like forgetting to add a file to git!
    """
    print("🧪 Testing Slack integration file structure...")
    
    # ===== DEFINE EXPECTED STRUCTURE =====
    base_path = Path("slack")
    required_files = [
        "slack_bot.py",           # Main bot implementation
        "slack_formatters.py",    # Message formatting functions
        "slack_utils.py",         # Utility functions and helpers
        "notifications.py",       # Notification management system
        "start_slack_bot.py",     # Production startup script
        "requirements.txt"        # Slack-specific dependencies
    ]
    
    success = True
    
    # ===== CHECK SLACK DIRECTORY EXISTS =====
    if not base_path.exists():
        print(f"❌ Slack directory not found: {base_path}")
        return False
    
    # ===== CHECK EACH REQUIRED FILE =====
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {full_path}")
            success = False
        else:
            print(f"✅ Found: {full_path}")
    
    return success

# ==========================================
# 🔧 CODE QUALITY VALIDATION
# ==========================================

def test_slack_bot_imports():
    """
    🧪 Test that all Slack bot imports work correctly
    
    🎯 PURPOSE: Catch syntax errors and missing dependencies early
    
    WHAT WE TEST:
    - Python syntax is valid (files can be parsed)
    - All required classes and functions exist
    - No obvious import errors or typos
    
    TESTING APPROACH:
    1. Use importlib to load modules dynamically
    2. Check for expected classes/functions
    3. Verify core functionality is accessible
    
    💡 ADHD TIP: Import tests catch typos and missing functions before runtime
    """
    print("🧪 Testing Slack bot imports...")
    
    try:
        # ===== PREPARE IMPORT PATH =====
        # Add slack directory to Python path for imports
        sys.path.insert(0, str(Path("slack")))
        
        # ===== TEST MAIN BOT FILE =====
        import importlib.util
        
        # Test slack_bot.py - main bot implementation
        slack_bot_spec = importlib.util.spec_from_file_location(
            "slack_bot", "slack/slack_bot.py"
        )
        if slack_bot_spec is None:
            print("❌ Cannot load slack_bot.py")
            return False
        
        # Actually load and execute the module
        slack_bot_module = importlib.util.module_from_spec(slack_bot_spec)
        slack_bot_spec.loader.exec_module(slack_bot_module)
        
        # ===== VERIFY MAIN CLASS EXISTS =====
        if not hasattr(slack_bot_module, 'JamieSlackBot'):
            print("❌ JamieSlackBot class not found in slack_bot.py")
            return False
        
        print("✅ slack_bot.py imports successfully")
        
        # ===== TEST FORMATTERS FILE =====
        formatters_spec = importlib.util.spec_from_file_location(
            "slack_formatters", "slack/slack_formatters.py"
        )
        formatters_module = importlib.util.module_from_spec(formatters_spec)
        formatters_spec.loader.exec_module(formatters_module)
        
        # Check for required formatting functions
        required_functions = [
            'format_cluster_status',    # Kubernetes + Prometheus status
            'format_error_analysis',    # Error log formatting
            'format_metrics_summary',   # Performance metrics display
            'format_alert_summary'      # Alert notifications
        ]
        
        for func_name in required_functions:
            if not hasattr(formatters_module, func_name):
                print(f"❌ Function {func_name} not found in slack_formatters.py")
                return False
        
        print("✅ slack_formatters.py imports successfully")
        
        # ===== TEST UTILITIES FILE =====
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        # Check for core utility functions
        required_utils = [
            'extract_devops_intent',     # Natural language processing
            'get_user_preferences',      # User settings management
            'save_user_preferences',     # Preference persistence
            'sync_with_portal'          # Cross-platform integration
        ]
        
        for util_name in required_utils:
            if not hasattr(utils_module, util_name):
                print(f"❌ Function {util_name} not found in slack_utils.py")
                return False
        
        print("✅ slack_utils.py imports successfully")
        
        # ===== TEST NOTIFICATIONS FILE =====
        notifications_spec = importlib.util.spec_from_file_location(
            "notifications", "slack/notifications.py"
        )
        notifications_module = importlib.util.module_from_spec(notifications_spec)
        notifications_spec.loader.exec_module(notifications_module)
        
        # Check for notification manager class
        if not hasattr(notifications_module, 'JamieNotificationManager'):
            print("❌ JamieNotificationManager class not found in notifications.py")
            return False
        
        print("✅ notifications.py imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

# ==========================================
# ⚙️ CONFIGURATION VALIDATION  
# ==========================================

def test_slack_configuration():
    """
    🧪 Test Slack configuration and environment setup
    
    🎯 PURPOSE: Validate configuration loading and credential validation
    
    WHAT WE TEST:
    - Configuration loading logic works
    - Credential validation catches bad tokens
    - Environment variable handling is robust
    - Error messages are helpful
    
    TEST STRATEGY:
    1. Test configuration with missing environment variables
    2. Test credential validation with good/bad tokens
    3. Verify error handling and user guidance
    
    💡 ADHD TIP: Configuration tests prevent "it works on my machine" problems
    """
    print("🧪 Testing Slack configuration...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        # ===== LOAD STARTUP MODULE =====
        startup_spec = importlib.util.spec_from_file_location(
            "start_slack_bot", "slack/start_slack_bot.py"
        )
        startup_module = importlib.util.module_from_spec(startup_spec)
        startup_spec.loader.exec_module(startup_module)
        
        # ===== CHECK BOOTSTRAP CLASS EXISTS =====
        if not hasattr(startup_module, 'JamieSlackBootstrap'):
            print("❌ JamieSlackBootstrap class not found")
            return False
        
        # ===== TEST CONFIGURATION LOADING =====
        bootstrap = startup_module.JamieSlackBootstrap()
        
        # This should return None due to missing env vars (expected behavior)
        config = bootstrap._load_configuration()
        if config is not None:
            print("⚠️ Configuration loaded without environment variables (unexpected)")
        
        print("✅ Configuration structure is valid")
        
        # ===== TEST CREDENTIAL VALIDATION =====
        # Test with valid credential format
        test_config = {
            'bot_token': 'xoxb-test-token',        # Correct format
            'app_token': 'xapp-test-token',        # Correct format
            'signing_secret': 'a' * 32             # Minimum length requirement
        }
        
        if not bootstrap._validate_slack_credentials(test_config):
            print("❌ Credential validation failed for valid test config")
            return False
        
        # ===== TEST INVALID CREDENTIALS =====
        # Test with bad credential format
        invalid_config = {
            'bot_token': 'invalid-token',          # Wrong format
            'app_token': 'invalid-token',          # Wrong format
            'signing_secret': 'short'              # Too short
        }
        
        if bootstrap._validate_slack_credentials(invalid_config):
            print("❌ Credential validation passed for invalid config")
            return False
        
        print("✅ Credential validation works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

# ==========================================
# 🧠 LOGIC FUNCTIONALITY TESTS
# ==========================================

def test_devops_intent_extraction():
    """
    🧪 Test DevOps intent extraction accuracy
    
    🎯 PURPOSE: Verify Jamie can understand what users want from natural language
    
    WHAT WE TEST:
    - Cluster status queries are recognized correctly
    - Error investigation requests are identified
    - Performance monitoring questions are parsed
    - Entity extraction finds services, time ranges, etc.
    - Priority detection works (urgent vs normal)
    
    TEST CASES:
    - "How's my cluster?" → cluster_status intent
    - "Show me errors from auth-service" → error_investigation + service entity
    - "CPU usage last hour" → performance_monitoring + time range
    
    💡 ADHD TIP: Intent extraction is Jamie's "listening comprehension" - crucial for good responses!
    """
    print("🧪 Testing DevOps intent extraction...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        # ===== LOAD UTILS MODULE =====
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        # ===== TEST CLUSTER STATUS QUERIES =====
        cluster_queries = [
            "How's my cluster doing?",
            "What's the cluster status?",
            "Show me cluster health"
        ]
        
        for query in cluster_queries:
            result = utils_module.extract_devops_intent(query)
            if result.get("intent") != "cluster_status":
                print(f"❌ Failed to detect cluster_status intent for: '{query}'")
                print(f"   Got: {result.get('intent')}")
                return False
        
        print("✅ Cluster status intent detection works")
        
        # ===== TEST ERROR INVESTIGATION =====
        error_queries = [
            "Show me errors from auth-service",
            "What's wrong with the API?",
            "Debug the payment service"
        ]
        
        for query in error_queries:
            result = utils_module.extract_devops_intent(query)
            if result.get("intent") != "error_investigation":
                print(f"❌ Failed to detect error_investigation intent for: '{query}'")
                return False
        
        print("✅ Error investigation intent detection works")
        
        # ===== TEST ENTITY EXTRACTION =====
        # Test service name extraction
        service_query = "show me errors from auth-service last hour"
        result = utils_module.extract_devops_intent(service_query)
        
        entities = result.get("entities", {})
        if "service_names" not in entities:
            print("❌ Failed to extract service names from query")
            return False
        
        if "auth" not in entities["service_names"]:  # Should match "auth-service" pattern
            print("❌ Failed to extract 'auth' service name")
            return False
        
        print("✅ Service name extraction works")
        
        # ===== TEST TIME RANGE EXTRACTION =====
        time_query = "show me logs from the last 2 hours"
        result = utils_module.extract_devops_intent(time_query)
        
        if result.get("time_range") != "2h":
            print(f"❌ Failed to extract time range. Got: {result.get('time_range')}")
            return False
        
        print("✅ Time range extraction works")
        
        # ===== TEST PRIORITY DETECTION =====
        # Critical priority
        urgent_query = "URGENT: database is down!"
        result = utils_module.extract_devops_intent(urgent_query)
        
        if result.get("priority") != "high":
            print(f"❌ Failed to detect high priority. Got: {result.get('priority')}")
            return False
        
        # Normal priority
        normal_query = "How's the CPU usage?"
        result = utils_module.extract_devops_intent(normal_query)
        
        if result.get("priority") != "normal":
            print(f"❌ Failed to detect normal priority. Got: {result.get('priority')}")
            return False
        
        print("✅ Priority detection works")
        
        return True
        
    except Exception as e:
        print(f"❌ Intent extraction test error: {e}")
        return False

def test_slack_formatting():
    """Test Slack message formatting functions"""
    print("🧪 Testing Slack message formatting...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        formatters_spec = importlib.util.spec_from_file_location(
            "slack_formatters", "slack/slack_formatters.py"
        )
        formatters_module = importlib.util.module_from_spec(formatters_spec)
        formatters_spec.loader.exec_module(formatters_module)
        
        # Test cluster status formatting
        test_k8s_status = {
            "healthy": True,
            "nodes_ready": 3,
            "nodes_total": 3,
            "pods_running": 15,
            "services_count": 8
        }
        
        test_prometheus_status = {
            "firing_alerts": 0
        }
        
        cluster_blocks = formatters_module.format_cluster_status(
            test_k8s_status, test_prometheus_status
        )
        
        if not isinstance(cluster_blocks, list):
            print("❌ format_cluster_status should return a list")
            return False
        
        if len(cluster_blocks) == 0:
            print("❌ format_cluster_status returned empty list")
            return False
        
        # Check for required block structure
        has_header = any(block.get("type") == "header" for block in cluster_blocks)
        has_actions = any(block.get("type") == "actions" for block in cluster_blocks)
        
        if not has_header:
            print("❌ Cluster status blocks missing header")
            return False
        
        if not has_actions:
            print("❌ Cluster status blocks missing actions")
            return False
        
        print("✅ Cluster status formatting works correctly")
        
        # Test error analysis formatting
        test_errors = [
            {
                "service": "auth-service",
                "message": "Connection timeout",
                "severity": "error",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
        
        error_blocks = formatters_module.format_error_analysis(test_errors)
        
        if not isinstance(error_blocks, list) or len(error_blocks) == 0:
            print("❌ format_error_analysis failed")
            return False
        
        print("✅ Error analysis formatting works correctly")
        
        # Test metrics formatting
        test_metrics = {
            "cpu": {"current": 65.2},
            "memory": {"current": 72.8},
            "disk": {"current": 45.0}
        }
        
        metrics_blocks = formatters_module.format_metrics_summary(test_metrics)
        
        if not isinstance(metrics_blocks, list) or len(metrics_blocks) == 0:
            print("❌ format_metrics_summary failed")
            return False
        
        print("✅ Metrics formatting works correctly")
        
        # Test usage bar creation
        usage_bar = formatters_module.create_usage_bar(75.0)
        if not isinstance(usage_bar, str) or len(usage_bar) == 0:
            print("❌ create_usage_bar failed")
            return False
        
        print("✅ Usage bar creation works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Formatting test error: {e}")
        return False

def test_notification_system():
    """Test notification system structure"""
    print("🧪 Testing notification system...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        notifications_spec = importlib.util.spec_from_file_location(
            "notifications", "slack/notifications.py"
        )
        notifications_module = importlib.util.module_from_spec(notifications_spec)
        notifications_spec.loader.exec_module(notifications_module)
        
        # Check for required enums
        if not hasattr(notifications_module, 'NotificationSeverity'):
            print("❌ NotificationSeverity enum not found")
            return False
        
        if not hasattr(notifications_module, 'NotificationType'):
            print("❌ NotificationType enum not found")
            return False
        
        # Check for main notification manager class
        if not hasattr(notifications_module, 'JamieNotificationManager'):
            print("❌ JamieNotificationManager class not found")
            return False
        
        # Test enum values
        severity_enum = notifications_module.NotificationSeverity
        expected_severities = ['CRITICAL', 'WARNING', 'INFO', 'DEBUG']
        
        for severity in expected_severities:
            if not hasattr(severity_enum, severity):
                print(f"❌ Missing severity level: {severity}")
                return False
        
        print("✅ Notification enums are complete")
        
        # Test notification types
        type_enum = notifications_module.NotificationType
        expected_types = ['ALERT', 'INCIDENT', 'DEPLOYMENT', 'HEALTH_CHECK', 'PERFORMANCE']
        
        for notification_type in expected_types:
            if not hasattr(type_enum, notification_type):
                print(f"❌ Missing notification type: {notification_type}")
                return False
        
        print("✅ Notification types are complete")
        
        # Test manager methods
        manager_class = notifications_module.JamieNotificationManager
        
        # Mock slack client for testing
        mock_client = Mock()
        manager = manager_class(mock_client)
        
        required_methods = [
            'send_alert_notification',
            'send_incident_notification',
            'send_deployment_notification',
            'send_scheduled_summary',
            'send_proactive_insight'
        ]
        
        for method_name in required_methods:
            if not hasattr(manager, method_name):
                print(f"❌ Missing method: {method_name}")
                return False
        
        print("✅ Notification manager methods are complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification test error: {e}")
        return False

def test_cross_platform_sync():
    """Test cross-platform synchronization features"""
    print("🧪 Testing cross-platform synchronization...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        # Test session ID creation
        session_id = utils_module.create_session_id("user123", "channel456", "slack")
        
        if not isinstance(session_id, str) or len(session_id) == 0:
            print("❌ Session ID creation failed")
            return False
        
        # Test that same inputs produce same session ID
        session_id2 = utils_module.create_session_id("user123", "channel456", "slack")
        if session_id != session_id2:
            print("❌ Session ID not deterministic")
            return False
        
        print("✅ Session ID creation works correctly")
        
        # Test deep link creation
        deep_link = utils_module.create_deep_link("cluster_status")
        if not isinstance(deep_link, str) or "cluster_status" not in deep_link:
            print("❌ Deep link creation failed")
            return False
        
        # Test with parameters
        deep_link_with_params = utils_module.create_deep_link(
            "error_details", 
            {"service": "auth", "time": "1h"}
        )
        if "service=auth" not in deep_link_with_params:
            print("❌ Deep link with parameters failed")
            return False
        
        print("✅ Deep link creation works correctly")
        
        # Test notification context building
        test_data = {
            "id": "alert-123",
            "severity": "critical", 
            "summary": "High CPU usage"
        }
        
        context = utils_module.build_notification_context("alert", test_data)
        
        required_fields = ["event_type", "timestamp", "severity", "summary"]
        for field in required_fields:
            if field not in context:
                print(f"❌ Missing field in notification context: {field}")
                return False
        
        print("✅ Notification context building works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-platform sync test error: {e}")
        return False

def test_british_personality():
    """Test British personality and language features"""
    print("🧪 Testing British personality features...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        # Test British greetings
        greeting = utils_module.get_british_greeting()
        if not isinstance(greeting, str) or len(greeting) == 0:
            print("❌ British greeting generation failed")
            return False
        
        print(f"✅ British greeting generated: '{greeting}'")
        
        # Test British response flavors
        flavor = utils_module.get_british_response_flavor()
        if not isinstance(flavor, str) or len(flavor) == 0:
            print("❌ British response flavor generation failed")
            return False
        
        print(f"✅ British response flavor generated: '{flavor}'")
        
        # Test time formatting
        from datetime import datetime, timedelta
        
        # Test various time differences
        now = datetime.now()
        
        # Test "just now"
        recent_time = now - timedelta(seconds=30)
        time_str = utils_module.format_time_ago(recent_time)
        if "just now" not in time_str:
            print(f"❌ Time formatting failed for recent time: {time_str}")
            return False
        
        # Test "minutes ago"
        minutes_ago = now - timedelta(minutes=5)
        time_str = utils_module.format_time_ago(minutes_ago)
        if "minute" not in time_str:
            print(f"❌ Time formatting failed for minutes: {time_str}")
            return False
        
        print("✅ British time formatting works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ British personality test error: {e}")
        return False

def test_requirements_and_dependencies():
    """Test that all requirements are properly specified"""
    print("🧪 Testing requirements and dependencies...")
    
    # Check Slack-specific requirements
    slack_requirements = Path("slack/requirements.txt")
    if not slack_requirements.exists():
        print("❌ Slack requirements.txt not found")
        return False
    
    # Read requirements
    with open(slack_requirements) as f:
        slack_deps = f.read()
    
    required_packages = [
        "slack-bolt",
        "slack-sdk", 
        "psutil",
        "aiohttp"
    ]
    
    for package in required_packages:
        if package not in slack_deps:
            print(f"❌ Missing required package in slack requirements: {package}")
            return False
    
    print("✅ Slack requirements are complete")
    
    # Check main requirements update
    main_requirements = Path("requirements.txt")
    if main_requirements.exists():
        with open(main_requirements) as f:
            main_deps = f.read()
        
        if "slack-bolt" not in main_deps:
            print("⚠️ Main requirements.txt not updated with Slack dependencies")
        else:
            print("✅ Main requirements include Slack dependencies")
    
    return True

def test_slack_app_configuration():
    """Test Slack app configuration and manifest"""
    print("🧪 Testing Slack app configuration...")
    
    # This test checks for the presence of configuration guidance
    startup_script = Path("slack/start_slack_bot.py")
    if not startup_script.exists():
        print("❌ Startup script not found")
        return False
    
    with open(startup_script) as f:
        startup_content = f.read()
    
    # Check for configuration guidance
    required_elements = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "print_setup_instructions",
        "api.slack.com/apps"
    ]
    
    for element in required_elements:
        if element not in startup_content:
            print(f"❌ Missing configuration element: {element}")
            return False
    
    print("✅ Slack app configuration guidance is present")
    
    # Check for proper error handling
    error_handling_elements = [
        "validate_slack_credentials",
        "auth_test",
        "graceful_shutdown"
    ]
    
    for element in error_handling_elements:
        if element not in startup_content:
            print(f"❌ Missing error handling element: {element}")
            return False
    
    print("✅ Error handling is implemented")
    
    return True

# ==========================================
# 🧪 MAIN TEST RUNNER
# ==========================================

def run_all_tests():
    """
    🧪 Run all Sprint 5 Slack integration tests
    
    🎯 PURPOSE: Comprehensive validation of Jamie's Slack integration
    
    TEST SEQUENCE:
    1. File Structure → 2. Code Quality → 3. Configuration → 4. Logic → 5. Integration
    
    RESULTS:
    - Shows pass/fail for each test
    - Counts total success rate
    - Provides clear feedback for fixes needed
    
    💡 ADHD TIP: All tests in one place - run once, see everything that works or needs fixing!
    """
    
    print("🧪" + "="*60)
    print("🧪 Jamie AI DevOps Copilot - Sprint 5 Test Suite")
    print("🧪 Slack Integration - Comprehensive Validation")
    print("🧪" + "="*60)
    
    # ===== DEFINE ALL TESTS =====
    tests = [
        ("File Structure", test_slack_integration_structure),
        ("Code Imports", test_slack_bot_imports),
        ("Configuration", test_slack_configuration),
        ("Intent Extraction", test_devops_intent_extraction),
        ("Slack Formatting", test_slack_formatting),
        ("Notifications", test_notification_system),
        ("Cross-Platform Sync", test_cross_platform_sync),
        ("British Personality", test_british_personality),
        ("Dependencies", test_requirements_and_dependencies),
        ("Slack App Config", test_slack_app_configuration)
    ]
    
    # ===== RUN EACH TEST =====
    passed = 0
    total = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n🧪 Running Test: {test_name}")
        print("-" * 50)
        
        try:
            # Run the test function
            result = test_function()
            
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # ===== DISPLAY RESULTS =====
    print("\n" + "="*60)
    print("🧪 TEST RESULTS SUMMARY")
    print("="*60)
    
    success_rate = (passed / total) * 100
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Sprint 5 Slack integration is ready! 🚀")
        print("🇬🇧 Jamie says: 'Brilliant! Everything's working like a dream, mate!'")
    else:
        failed = total - passed
        print(f"⚠️ {failed} test(s) failed. Please review and fix issues above.")
        print("🇬🇧 Jamie says: 'Bit of a wobble, but we'll sort it out!'")
    
    return passed == total

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    """
    🎯 Run this script to validate Sprint 5 Slack integration
    
    USAGE:
    python test_jamie_sprint5.py
    
    💡 ADHD TIP: Single command to test everything - no need to remember multiple test commands!
    """
    
    try:
        # Set up proper working directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Run all tests
        success = run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1) 