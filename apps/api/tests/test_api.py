from __future__ import annotations

from app.services.analysis_pipeline import AnalysisPipeline
from tests.helpers import sample_resume_text


def test_analysis_api_happy_path(client):
    response = client.post(
        "/api/analyses",
        files={"file": ("resume.txt", sample_resume_text().encode("utf-8"), "text/plain")},
        data={
            "job_text": """
Senior Backend Engineer
Example Co

Responsibilities
Build backend APIs and internal tools.

Requirements
Python
FastAPI
3+ years of experience

Preferred
Kubernetes
""",
            "job_label": "Senior Backend Engineer",
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    analysis_id = payload["id"]
    assert payload["overall_score"] >= 0
    assert payload["requirements"]
    assert payload["suggestions"]

    listing = client.get("/api/analyses")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    parsed_resume = client.get(f"/api/analyses/{analysis_id}/parsed-resume")
    assert parsed_resume.status_code == 200
    assert parsed_resume.json()["skills"]

    score = client.get(f"/api/analyses/{analysis_id}/score")
    assert score.status_code == 200
    assert score.json()["subscores"]

    delete_response = client.delete(f"/api/analyses/{analysis_id}")
    assert delete_response.status_code == 204
    assert client.get("/api/analyses").json() == []


def test_analysis_api_rejects_blank_inputs(client):
    blank_job = client.post("/api/jobs/parse-text", json={"job_text": "   "})
    assert blank_job.status_code == 400
    assert blank_job.json()["detail"] == "Job description cannot be empty"

    blank_resume = client.post(
        "/api/analyses",
        files={"file": ("resume.txt", b"   \n\n", "text/plain")},
        data={"job_text": "Backend Engineer"},
    )
    assert blank_resume.status_code == 400
    assert blank_resume.json()["detail"] == "No readable text found in the uploaded document"


def test_analysis_api_hides_unexpected_server_errors(client, monkeypatch):
    def crash(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(AnalysisPipeline, "run", crash)

    response = client.post(
        "/api/analyses",
        files={"file": ("resume.txt", sample_resume_text().encode("utf-8"), "text/plain")},
        data={"job_text": "Backend Engineer"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Analysis failed due to an unexpected server error"
