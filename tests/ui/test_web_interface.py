"""
UI tests for the web interface using Playwright.
"""
import pytest
import os
from typing import Any, Dict, Generator

from playwright.sync_api import Playwright, Browser, Page, expect

# Configuration for test environment
TEST_URL = os.environ.get("TEST_URL", "http://localhost:8080")
USERNAME = os.environ.get("TEST_USERNAME", "admin")
PASSWORD = os.environ.get("TEST_PASSWORD", "admin")


@pytest.fixture
def logged_in_page(playwright: Playwright) -> Generator[Page, None, None]:
    """Create a logged-in page fixture."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Go to application and log in
    page.goto(TEST_URL)
    
    # Check if login modal is visible
    if page.is_visible("#login-modal"):
        page.fill("#username", USERNAME)
        page.fill("#password", PASSWORD)
        page.click("#login-form button[type='submit']")
        
        # Wait for login to complete
        page.wait_for_selector(".app-container", state="visible")
    
    # Verify we're logged in by checking for dashboard
    expect(page.locator(".app-container")).to_be_visible()
    
    yield page
    
    # Clean up
    context.close()
    browser.close()


def test_dashboard(logged_in_page: Page) -> None:
    """Test the dashboard page."""
    page = logged_in_page
    
    # Check dashboard elements
    expect(page.locator(".stats-container")).to_be_visible()
    expect(page.locator(".dashboard-grid")).to_be_visible()
    
    # Check stat cards
    stat_cards = page.locator(".stat-card")
    expect(stat_cards).to_have_count(4)
    
    # Check if system status section exists
    expect(page.locator("#system-status")).to_be_visible()


def test_calls_page(logged_in_page: Page) -> None:
    """Test the calls page."""
    page = logged_in_page
    
    # Navigate to calls page
    page.click("nav.sidebar a[data-page='calls']")
    
    # Verify calls page is loaded
    expect(page.locator("#calls")).to_be_visible()
    expect(page.locator(".calls-container")).to_be_visible()
    
    # Check filters
    expect(page.locator("#call-status-filter")).to_be_visible()
    expect(page.locator("#call-date-filter")).to_be_visible()
    
    # Check calls table
    expect(page.locator("#calls-table")).to_be_visible()
    
    # Test filter functionality
    page.select_option("#call-status-filter", "completed")
    
    # Pagination controls should be visible
    expect(page.locator(".pagination")).to_be_visible()


def test_messages_page(logged_in_page: Page) -> None:
    """Test the messages page."""
    page = logged_in_page
    
    # Navigate to messages page
    page.click("nav.sidebar a[data-page='messages']")
    
    # Verify messages page is loaded
    expect(page.locator("#messages")).to_be_visible()
    expect(page.locator(".messages-container")).to_be_visible()
    
    # Check filters
    expect(page.locator("#message-urgency-filter")).to_be_visible()
    expect(page.locator("#message-date-filter")).to_be_visible()
    
    # Check new message button
    expect(page.locator("#new-message-btn")).to_be_visible()
    
    # Test new message functionality
    page.click("#new-message-btn")
    expect(page.locator("#message-form-modal")).to_be_visible()
    
    # Close the modal
    page.click("#message-form-modal .close-btn")
    expect(page.locator("#message-form-modal")).not_to_be_visible()


def test_appointments_page(logged_in_page: Page) -> None:
    """Test the appointments page."""
    page = logged_in_page
    
    # Navigate to appointments page
    page.click("nav.sidebar a[data-page='appointments']")
    
    # Verify appointments page is loaded
    expect(page.locator("#appointments")).to_be_visible()
    expect(page.locator(".appointments-container")).to_be_visible()
    
    # Check filters
    expect(page.locator("#appointment-status-filter")).to_be_visible()
    expect(page.locator("#appointment-date-filter")).to_be_visible()
    
    # Check calendar and list views
    expect(page.locator("#appointments-calendar")).to_be_visible()
    expect(page.locator("#appointments-list")).to_be_visible()
    
    # Test new appointment functionality
    page.click("#new-appointment-btn")
    expect(page.locator("#appointment-form-modal")).to_be_visible()
    
    # Close the modal
    page.click("#appointment-form-modal .close-btn")
    expect(page.locator("#appointment-form-modal")).not_to_be_visible()


def test_settings_page(logged_in_page: Page) -> None:
    """Test the settings page."""
    page = logged_in_page
    
    # Navigate to settings page
    page.click("nav.sidebar a[data-page='settings']")
    
    # Verify settings page is loaded
    expect(page.locator("#settings")).to_be_visible()
    expect(page.locator(".settings-container")).to_be_visible()
    
    # Check settings navigation
    settings_nav = page.locator(".settings-nav a")
    expect(settings_nav).to_have_count(6)  # 6 settings categories
    
    # Test navigation between settings panels
    page.click(".settings-nav a[data-settings='voice']")
    expect(page.locator("#voice-settings")).to_be_visible()
    
    page.click(".settings-nav a[data-settings='llm']")
    expect(page.locator("#llm-settings")).to_be_visible()


def test_end_to_end_workflow(logged_in_page: Page) -> None:
    """Test an end-to-end workflow."""
    page = logged_in_page
    
    # 1. Navigate to dashboard
    page.click("nav.sidebar a[data-page='dashboard']")
    expect(page.locator("#dashboard")).to_be_visible()
    
    # 2. Navigate to calls page
    page.click("nav.sidebar a[data-page='calls']")
    expect(page.locator("#calls")).to_be_visible()
    
    # 3. Create a message (dummy action since we can't create a real call in UI tests)
    page.click("nav.sidebar a[data-page='messages']")
    expect(page.locator("#messages")).to_be_visible()
    page.click("#new-message-btn")
    
    # Fill message form
    page.fill("#message-recipient", "test@example.com")
    page.fill("#message-subject", "Test message from UI tests")
    page.fill("#message-content", "This is a test message created during UI testing.")
    page.select_option("#message-urgency", "high")
    
    # Submit form (note: in a real test with API, we'd expect this to succeed)
    page.click("#send-message-btn")
    
    # 4. Create an appointment
    page.click("nav.sidebar a[data-page='appointments']")
    expect(page.locator("#appointments")).to_be_visible()
    page.click("#new-appointment-btn")
    
    # Fill appointment form
    page.fill("#appointment-title", "Test Appointment")
    page.fill("#appointment-contact", "Test Contact")
    
    # Tomorrow's date
    import datetime
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    page.fill("#appointment-date", tomorrow.strftime("%Y-%m-%d"))
    
    page.fill("#appointment-start-time", "14:00")
    page.fill("#appointment-end-time", "15:00")
    page.fill("#appointment-notes", "Test appointment from UI tests")
    
    # Submit form
    page.click("#save-appointment-btn")
    
    # 5. Check settings
    page.click("nav.sidebar a[data-page='settings']")
    expect(page.locator("#settings")).to_be_visible()
    
    # Check general settings
    expect(page.locator("#general-settings-form")).to_be_visible()
    
    # 6. Return to dashboard
    page.click("nav.sidebar a[data-page='dashboard']")
    expect(page.locator("#dashboard")).to_be_visible()
    
    # Check for recent activities (might not exist in test environment)
    expect(page.locator(".dashboard-grid")).to_be_visible()