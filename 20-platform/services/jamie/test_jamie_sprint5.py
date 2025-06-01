#!/usr/bin/env python3
"""
🧪 Jamie AI DevOps Copilot - Sprint 5 Test Suite
Slack Integration - Comprehensive Validation

Tests all components of the Slack integration:
- Slack bot setup and configuration
- Slash commands and interactive components
- Notifications and alert system
- Cross-platform synchronization
- Team collaboration features
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
import unittest
from unittest.mock import Mock, AsyncMock, patch

def test_slack_integration_structure():
    """Test that the Slack integration directory structure is correct"""
    print("🧪 Testing Slack integration file structure...")
    
    base_path = Path("slack")
    required_files = [
        "slack_bot.py",
        "slack_formatters.py", 
        "slack_utils.py",
        "notifications.py",
        "start_slack_bot.py",
        "requirements.txt"
    ]
    
    success = True
    
    # Check if slack directory exists
    if not base_path.exists():
        print(f"❌ Slack directory not found: {base_path}")
        return False
    
    # Check required files
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {full_path}")
            success = False
        else:
            print(f"✅ Found: {full_path}")
    
    return success

def test_slack_bot_imports():
    """Test that all Slack bot imports work correctly"""
    print("🧪 Testing Slack bot imports...")
    
    try:
        # Test import of main bot class
        sys.path.insert(0, str(Path("slack")))
        
        # Check if we can import the main classes (would fail if syntax errors)
        import importlib.util
        
        # Test slack_bot.py
        slack_bot_spec = importlib.util.spec_from_file_location(
            "slack_bot", "slack/slack_bot.py"
        )
        if slack_bot_spec is None:
            print("❌ Cannot load slack_bot.py")
            return False
        
        slack_bot_module = importlib.util.module_from_spec(slack_bot_spec)
        slack_bot_spec.loader.exec_module(slack_bot_module)
        
        # Check for main class
        if not hasattr(slack_bot_module, 'JamieSlackBot'):
            print("❌ JamieSlackBot class not found in slack_bot.py")
            return False
        
        print("✅ slack_bot.py imports successfully")
        
        # Test slack_formatters.py
        formatters_spec = importlib.util.spec_from_file_location(
            "slack_formatters", "slack/slack_formatters.py"
        )
        formatters_module = importlib.util.module_from_spec(formatters_spec)
        formatters_spec.loader.exec_module(formatters_module)
        
        required_functions = [
            'format_cluster_status',
            'format_error_analysis', 
            'format_metrics_summary',
            'format_alert_summary'
        ]
        
        for func_name in required_functions:
            if not hasattr(formatters_module, func_name):
                print(f"❌ Function {func_name} not found in slack_formatters.py")
                return False
        
        print("✅ slack_formatters.py imports successfully")
        
        # Test slack_utils.py
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        required_utils = [
            'extract_devops_intent',
            'get_user_preferences',
            'save_user_preferences',
            'sync_with_portal'
        ]
        
        for util_name in required_utils:
            if not hasattr(utils_module, util_name):
                print(f"❌ Function {util_name} not found in slack_utils.py")
                return False
        
        print("✅ slack_utils.py imports successfully")
        
        # Test notifications.py
        notifications_spec = importlib.util.spec_from_file_location(
            "notifications", "slack/notifications.py"
        )
        notifications_module = importlib.util.module_from_spec(notifications_spec)
        notifications_spec.loader.exec_module(notifications_module)
        
        if not hasattr(notifications_module, 'JamieNotificationManager'):
            print("❌ JamieNotificationManager class not found in notifications.py")
            return False
        
        print("✅ notifications.py imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_slack_configuration():
    """Test Slack configuration and environment setup"""
    print("🧪 Testing Slack configuration...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        # Load the startup script
        startup_spec = importlib.util.spec_from_file_location(
            "start_slack_bot", "slack/start_slack_bot.py"
        )
        startup_module = importlib.util.module_from_spec(startup_spec)
        startup_spec.loader.exec_module(startup_module)
        
        # Check for required configuration
        if not hasattr(startup_module, 'JamieSlackBootstrap'):
            print("❌ JamieSlackBootstrap class not found")
            return False
        
        # Test configuration loading (without actual env vars)
        bootstrap = startup_module.JamieSlackBootstrap()
        
        # This should return None due to missing env vars, but shouldn't crash
        config = bootstrap._load_configuration()
        if config is not None:
            print("⚠️ Configuration loaded without environment variables (unexpected)")
        
        print("✅ Configuration structure is valid")
        
        # Test credential validation
        test_config = {
            'bot_token': 'xoxb-test-token',
            'app_token': 'xapp-test-token',
            'signing_secret': 'a' * 32  # Minimum length
        }
        
        if not bootstrap._validate_slack_credentials(test_config):
            print("❌ Credential validation failed for valid test config")
            return False
        
        # Test invalid credentials
        invalid_config = {
            'bot_token': 'invalid-token',
            'app_token': 'invalid-token',
            'signing_secret': 'short'
        }
        
        if bootstrap._validate_slack_credentials(invalid_config):
            print("❌ Credential validation passed for invalid config")
            return False
        
        print("✅ Credential validation works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_devops_intent_extraction():
    """Test DevOps intent extraction functionality"""
    print("🧪 Testing DevOps intent extraction...")
    
    try:
        sys.path.insert(0, str(Path("slack")))
        import importlib.util
        
        utils_spec = importlib.util.spec_from_file_location(
            "slack_utils", "slack/slack_utils.py"
        )
        utils_module = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_module)
        
        # Test various DevOps queries
        test_cases = [
            {
                "query": "How's my cluster doing?",
                "expected_intent": "cluster_status",
                "expected_confidence": 0.8
            },
            {
                "query": "Show me recent errors",
                "expected_intent": "error_investigation",
                "expected_confidence": 0.8
            },
            {
                "query": "What's the CPU usage?",
                "expected_intent": "performance_monitoring",
                "expected_confidence": 0.8
            },
            {
                "query": "Any alerts firing?",
                "expected_intent": "alert_management",
                "expected_confidence": 0.8
            },
            {
                "query": "Hello there",
                "expected_intent": "general",
                "expected_confidence": 0.0
            }
        ]
        
        success = True
        for test_case in test_cases:
            result = utils_module.extract_devops_intent(test_case["query"])
            
            if result["intent"] != test_case["expected_intent"]:
                print(f"❌ Intent mismatch for '{test_case['query']}': got {result['intent']}, expected {test_case['expected_intent']}")
                success = False
            elif result["confidence"] != test_case["expected_confidence"]:
                print(f"⚠️ Confidence mismatch for '{test_case['query']}': got {result['confidence']}, expected {test_case['expected_confidence']}")
            else:
                print(f"✅ Intent extraction correct for: '{test_case['query']}'")
        
        # Test keyword extraction
        test_query = "Show me kubernetes pod errors from the last hour"
        result = utils_module.extract_devops_intent(test_query)
        
        expected_keywords = ["kubernetes", "pod", "error"]
        found_keywords = result.get("keywords", [])
        
        for keyword in expected_keywords:
            if keyword not in found_keywords:
                print(f"❌ Missing keyword '{keyword}' in extraction")
                success = False
        
        if success:
            print("✅ Keyword extraction working correctly")
        
        return success
        
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

def run_all_tests():
    """Run all Sprint 5 tests"""
    print("🚀 Running Jamie AI DevOps Copilot - Sprint 5 Test Suite")
    print("=" * 60)
    
    tests = [
        ("Slack Integration Structure", test_slack_integration_structure),
        ("Slack Bot Imports", test_slack_bot_imports),
        ("Slack Configuration", test_slack_configuration),
        ("DevOps Intent Extraction", test_devops_intent_extraction),
        ("Slack Message Formatting", test_slack_formatting),
        ("Notification System", test_notification_system),
        ("Cross-Platform Sync", test_cross_platform_sync),
        ("British Personality", test_british_personality),
        ("Requirements & Dependencies", test_requirements_and_dependencies),
        ("Slack App Configuration", test_slack_app_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"💥 {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SPRINT 5 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Jamie's Slack Integration is ready!")
        print("🤖 Sprint 5: Slack Integration - COMPLETE! 🇬🇧")
        print("\n💡 Next Steps:")
        print("   1. Set up Slack app at https://api.slack.com/apps")
        print("   2. Configure environment variables")
        print("   3. Run: python slack/start_slack_bot.py")
        print("   4. Use /jamie in Slack to start chatting!")
    else:
        print(f"⚠️ {total - passed} tests failed. Please fix issues before deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 