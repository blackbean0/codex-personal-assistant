"""End-to-end checks using synthetic inputs and an isolated database."""
import http.client
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from pa import db, jobs, materials, server


def run(with_ai=False, with_browser=False):
    from playwright.sync_api import sync_playwright

    original = (db.PATH, jobs.REPORT_DIR, jobs.student, materials._cfg, materials.open_file, materials.reveal, server.ALLOWED_HOSTS)
    with tempfile.TemporaryDirectory(prefix="pa-smoke-") as temp:
        root = Path(temp)
        db.PATH = root / "pa.db"
        jobs.REPORT_DIR = root / "report"
        jobs.REPORT_DIR.mkdir()
        (jobs.REPORT_DIR / "AGENTS.md").write_text("Write only using the supplied facts. No tool calls are needed.", encoding="utf-8")
        jobs.student = lambda: ("0000", "Example")
        materials._cfg = lambda: {"root": root, "courses": []}
        materials.open_file = lambda p: None
        materials.reveal = lambda p: None
        conn = db.connect()
        conn.execute("INSERT INTO notices (id, course, title, text, posted_at) "
                     "VALUES ('smoke', 'Example', 'Practice', 'Read chapter one.', '2026-11-16')")
        conn.commit()
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        port = httpd.server_address[1]
        server.ALLOWED_HOSTS = set(server.ALLOWED_HOSTS) | {f"127.0.0.1:{port}"}
        try:
            if with_ai:
                client = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                client.request("POST", "/api/job/notices", body="{}", headers={
                    "Host": "localhost:8765", "X-PA": "1", "Content-Type": "application/json"})
                response = client.getresponse()
                assert response.status == 200
                response.read()
                client.close()
                assert jobs.run_next(conn)
                assert jobs.recent(conn)[0]["status"] == "done", "AI notice job failed (details hidden)"
                assert conn.execute("SELECT summary FROM notices WHERE id='smoke'").fetchone()[0]
                print("Dashboard HTTP -> queue -> Codex -> summary: PASS")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    if with_browser:
                        page = browser.new_page()
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                        page.wait_for_timeout(300)
                        assert page.evaluate("D !== null && D.ai === 'Codex' && D.setup !== undefined")
                        # Render the changed job-count and cancellation UI with no paid call.
                        job = jobs.enqueue(conn, "notices", "pending", "Synthetic queued job")
                        page.evaluate("load()")
                        page.wait_for_timeout(300)
                        assert page.evaluate("D.jobs.some(j => j.ai_calls !== undefined)")
                        page.evaluate("UI.open.add('check'); render()")
                        page.locator(f'[data-act="jobcancel"][data-id="{job}"]').evaluate("button => button.click()")
                        page.wait_for_function("id => D.jobs.some(j => j.id === id && j.status === 'cancelled')", arg=job)
                        assert not errors, "Dashboard JavaScript failed (details hidden)"
                        page.close()
                        print("Chromium dashboard, setup state, job counts and cancel button: PASS")
                    if with_ai:
                        material = root / "materials" / "example" / "sample.pdf"
                        material.parent.mkdir(parents=True)
                        page = browser.new_page()
                        page.set_content("<h1>Example lesson</h1><p>The practice garden contains exactly seven trees.</p>")
                        page.pdf(path=str(material))
                        page.close()
                        from pa.documents import extract
                        assert "seven trees" in extract(material)
                        jobs.enqueue(conn, "summary", str(material), "Synthetic PDF")
                        assert jobs.run_next(conn)
                        assert jobs.recent(conn)[0]["status"] == "done", "AI PDF summary failed (details hidden)"
                        assert jobs.summary_path(material).is_file()
                        print("PDF extraction -> Codex -> saved summary: PASS")
                        db.sync_source(conn, "inbox", [{"key": "smoke-report", "kind": "assignment", "course": "Example",
                            "title": "Practice report", "due": "2099-01-01T00:00:00+09:00", "earliest": None, "minutes": 30, "url": ""}])
                        jobs.save_brief(conn, "smoke-report", "연습 정원의 나무는 정확히 일곱 그루다. 이 사실만 사용해 짧은 보고서를 쓴다.")
                        jobs.enqueue(conn, "report", "smoke-report", "Synthetic report")
                        assert jobs.run_next(conn)
                        result = jobs.recent(conn)[0]
                        assert result["status"] == "done", "AI report failed (details hidden)"
                        assert Path(result["result"]).is_file()
                        print("Report instructions -> Codex -> saved draft: PASS")
                finally:
                    browser.close()
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)
            conn.close()
            (db.PATH, jobs.REPORT_DIR, jobs.student, materials._cfg, materials.open_file,
             materials.reveal, server.ALLOWED_HOSTS) = original
