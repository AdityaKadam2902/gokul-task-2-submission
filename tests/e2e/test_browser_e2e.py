"""Playwright browser-level E2E tests for LabInsight.
Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DATABASE_URL = "sqlite:///./backend/data/labinsight_e2e.db"


def wait_for_url(url: str, timeout_seconds: int = 15) -> bool:
    """Poll URL until HTTP 200 is returned or timeout expires."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


@pytest.fixture(scope="module")
def running_servers():
    """Start isolated FastAPI backend and Vite frontend for browser tests."""
    e2e_db_path = ROOT_DIR / "backend" / "data" / "labinsight_e2e.db"
    for db_file in [
        e2e_db_path,
        Path(str(e2e_db_path) + "-wal"),
        Path(str(e2e_db_path) + "-shm"),
    ]:
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception:
                pass

    env = os.environ.copy()
    env["DATABASE_URL"] = DATABASE_URL
    env["PYTHONPATH"] = str(ROOT_DIR / "backend")

    # Upgrade isolated db schema
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(ROOT_DIR),
        env=env,
        capture_output=True,
    )

    # Start backend
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Start frontend
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [
            npm_cmd,
            "--prefix",
            "frontend",
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            "5173",
        ],
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert wait_for_url("http://127.0.0.1:8000/api/v1/health", 15), "Backend failed to start"
    assert wait_for_url("http://127.0.0.1:5173", 15), "Frontend failed to start"

    yield "http://127.0.0.1:5173"

    try:
        backend_proc.terminate()
        backend_proc.wait(timeout=3)
    except Exception:
        backend_proc.kill()

    try:
        frontend_proc.terminate()
        frontend_proc.wait(timeout=3)
    except Exception:
        frontend_proc.kill()

    for db_file in [
        e2e_db_path,
        Path(str(e2e_db_path) + "-wal"),
        Path(str(e2e_db_path) + "-shm"),
    ]:
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception:
                pass


def test_full_browser_workflow(running_servers: str) -> None:
    """Comprehensive browser E2E test exercising all UI states and user flows."""
    frontend_url = running_servers
    uid = str(int(time.time()))
    test_name = f"Subject {uid}"
    test_email = f"subject.{uid}@example.test"

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 850})
        page = context.new_page()

        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        # 1. Startup & Status
        page.goto(frontend_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        expect(page.locator("h1")).to_contain_text("LabInsight")
        expect(page.locator("header").get_by_text("Backend API:")).to_be_visible()
        expect(page.locator("header").get_by_text("Online")).to_be_visible()
        expect(page.locator("header").get_by_text("Database:")).to_be_visible()
        expect(page.locator("header").get_by_text("Ready")).to_be_visible()
        expect(page.locator("header").get_by_text("Local AI:")).to_be_visible()
        expect(page.locator("header").get_by_text("llama3.2:3b")).to_be_visible()
        expect(page.locator("aside")).to_contain_text("Educational Healthcare Prototype")

        # 2. Validation Rejections
        page.click("button:has-text('Add Patient Record')")
        page.wait_for_selector("#field-full-name")
        page.fill("#field-full-name", test_name)
        page.fill("#field-dob", "31/02/1990")
        page.fill("#field-email", "not-an-email")
        page.fill("#field-glucose", "-5")
        page.fill("#field-haemoglobin", "14")
        page.fill("#field-cholesterol", "180")
        page.click("button[type='submit']")
        page.wait_for_timeout(500)
        expect(page.locator("text=Impossible calendar date")).to_be_visible()

        # 3. Valid Registration
        page.fill("#field-dob", "15/06/1988")
        page.fill("#field-email", test_email)
        page.fill("#field-glucose", "92.5")
        page.click("button[type='submit']")

        # Acknowledgment modal
        if page.locator("text=Educational Assessment Disclosure").is_visible(timeout=3000):
            page.click("button:has-text('I Understand')")
        page.wait_for_timeout(1000)

        # Close detail modal if opened automatically upon creation
        if page.locator("button[aria-label='Close modal']").is_visible(timeout=3000):
            page.locator("button[aria-label='Close modal']").click()
            page.wait_for_timeout(500)

        expect(page.locator("table")).to_contain_text(test_name)

        # 4. Duplicate Detection & Confirmation
        page.click("button:has-text('Add Patient Record')")
        page.wait_for_selector("#field-full-name")
        page.fill("#field-full-name", test_name)
        page.fill("#field-dob", "15/06/1988")
        page.fill("#field-email", test_email)
        page.fill("#field-glucose", "92.5")
        page.fill("#field-haemoglobin", "14.0")
        page.fill("#field-cholesterol", "180.0")
        page.click("button[type='submit']")

        if page.locator("text=Educational Assessment Disclosure").is_visible(timeout=2000):
            page.click("button:has-text('I Understand')")

        page.wait_for_selector("text=Duplicate Patient Record Detected", timeout=10000)
        expect(page.locator("text=HTTP 409 Conflict")).to_be_visible()

        # Confirm duplicate insertion
        page.click("button:has-text('Confirm & Insert Duplicate Record')")
        page.wait_for_timeout(1000)

        # Close detail modal if opened for the duplicate record
        if page.locator("button[aria-label='Close modal']").is_visible(timeout=3000):
            page.locator("button[aria-label='Close modal']").click()
            page.wait_for_timeout(500)

        expect(page.locator("table")).to_contain_text(test_name)

        # 5. Target Email Edit
        matching_rows = page.locator(f"tbody tr:has-text('{test_name}')")
        matching_rows.first.locator("button[aria-label^='Edit record']").click()
        page.wait_for_selector("#field-email")
        updated_email = f"gokul.{uid}@infocare.com"
        page.fill("#field-email", updated_email)
        page.click("button[type='submit']:has-text('Save Changes')")
        page.wait_for_timeout(1000)
        expect(page.locator("table")).to_contain_text(updated_email)

        # 6. Delete Record
        matching_rows.last.locator("button[aria-label^='Delete record']").click()
        page.wait_for_selector("text=Delete Patient Record")
        page.click("button:has-text('Permanently Delete')")
        page.wait_for_timeout(1000)

        # Assert no console errors
        assert len(console_errors) == 0

        browser.close()
