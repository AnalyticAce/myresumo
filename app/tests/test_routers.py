"""Unit tests for FastAPI routers - comprehensive coverage."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from bson import ObjectId
from datetime import datetime
from app.main import app
from app.api.routers.resume import get_resume_repository
from app.api.routers.cover_letter import get_cover_letter_repository, get_ai_generator
from app.api.routers.comprehensive_optimizer import get_comprehensive_optimizer

client = TestClient(app)


@pytest.fixture
def mock_resume_repo():
    repo = MagicMock()
    repo.create_resume, repo.get_resume_by_id = AsyncMock(), AsyncMock()
    repo.get_resumes_by_user_id, repo.update_resume = AsyncMock(), AsyncMock()
    repo.delete_resume, repo.update_optimized_data = AsyncMock(), AsyncMock()
    return repo


@pytest.fixture
def mock_cl_repo():
    repo = MagicMock()
    repo.create_cover_letter, repo.get_cover_letter_by_id = AsyncMock(), AsyncMock()
    repo.get_cover_letters_by_user_id, repo.update_cover_letter = AsyncMock(), AsyncMock()
    repo.delete_cover_letter, repo.search_cover_letters = AsyncMock(), AsyncMock()
    repo.get_cover_letter_statistics = AsyncMock()
    return repo


@pytest.fixture
def mock_comp_optimizer():
    opt = MagicMock()
    opt.optimize_resume_master, opt.analyze_ats_keywords = AsyncMock(), AsyncMock()
    opt.extract_hidden_achievements, opt.create_three_versions = AsyncMock(), AsyncMock()
    opt.iterative_improvement = AsyncMock()
    opt.get_quick_start_workflows, opt.get_pro_tips = MagicMock(), MagicMock()
    opt.get_eu_2025_alignment, opt.MASTER_SKILLS_LIST = MagicMock(), "Skills"
    return opt


@pytest.fixture
def mock_ai_gen():
    gen = AsyncMock()
    gen.generate_cover_letter, gen.model_name = AsyncMock(), "test-model"
    return gen


@pytest.fixture
def override_deps(mock_resume_repo, mock_cl_repo, mock_comp_optimizer, mock_ai_gen):
    app.dependency_overrides[get_resume_repository] = lambda: mock_resume_repo
    app.dependency_overrides[get_cover_letter_repository] = lambda: mock_cl_repo
    app.dependency_overrides[get_comprehensive_optimizer] = lambda: mock_comp_optimizer
    app.dependency_overrides[get_ai_generator] = lambda: mock_ai_gen
    yield
    app.dependency_overrides.clear()

# === RESUME TESTS ===


def test_resume_upload(override_deps, mock_resume_repo):
    mock_resume_repo.create_resume.return_value = str(ObjectId())
    with patch("app.api.routers.resume.SecureFileValidator.validate_upload", AsyncMock(return_value=(b"t", "t.pdf", "h"))), \
            patch("app.api.routers.resume.store_file_securely", return_value="/t.pdf"), \
            patch("app.api.routers.resume.extract_text_from_file", return_value="E"):
        response = client.post("/api/resume/", data={"title": "T", "user_id": "u"}, files={
                               "file": ("t.pdf", b"t", "application/pdf")})
        assert response.status_code == 200


def test_get_user_resumes(override_deps, mock_resume_repo):
    now = datetime.now()
    mock_resume_repo.get_resumes_by_user_id.return_value = [
        {"_id": ObjectId(), "title": "A", "target_company": "Apple",
         "created_at": now, "updated_at": now},
        {"_id": ObjectId(), "title": "B", "target_company": "Google",
         "created_at": now, "updated_at": now}
    ]
    response = client.get(
        "/api/resume/user/u1?filter_company=Apple&sort_by=title&sort_order=desc")
    assert response.status_code == 200


def test_resume_crud(override_deps, mock_resume_repo):
    rid = str(ObjectId())
    mock_resume_repo.get_resume_by_id.return_value = {"_id": ObjectId(rid)}
    mock_resume_repo.update_resume.return_value = True
    mock_resume_repo.delete_resume.return_value = True

    assert client.put(f"/api/resume/{rid}/status/applied").status_code == 200
    assert client.put(f"/api/resume/{rid}",
                      json={"title": "N"}).status_code == 200
    assert client.delete(f"/api/resume/{rid}").status_code == 200


def test_resume_errors(override_deps, mock_resume_repo):
    mock_resume_repo.get_resume_by_id.return_value = None
    assert client.get(f"/api/resume/{str(ObjectId())}").status_code == 404
    assert client.get(
        f"/api/resume/{str(ObjectId())}/download").status_code == 404


def test_score_optimize(override_deps, mock_resume_repo):
    rid = str(ObjectId())
    mock_resume_repo.get_resume_by_id.return_value = {
        "_id": ObjectId(rid), "original_content": "C"}
    with patch("app.services.cv_analyzer.CVAnalyzer") as a, \
            patch("app.services.workflow_orchestrator.CVWorkflowOrchestrator") as o, \
            patch.dict("os.environ", {"API_BASE": "http://m"}):
        a.return_value.analyze.return_value = {
            "ats_score": 80, "matching_skills": []}
        o.return_value.optimize_cv_for_job.return_value = {
            "optimized_cv": {"user_information": {"name": "N", "main_job_title": "J", "profile_description": "D", "email": "e@e.com", "experiences": [], "education": [], "skills": {"hard_skills": [], "soft_skills": []}}},
            "ats_score": 90
        }
        assert client.post(
            f"/api/resume/{rid}/score", json={"job_description": "J"}).status_code == 200
        assert client.post(
            f"/api/resume/{rid}/optimize", json={"job_description": "J"}).status_code == 200

# === COVER LETTER TESTS ===


def test_create_cl(override_deps, mock_cl_repo):
    mock_cl_repo.create_cover_letter.return_value = str(ObjectId())
    response = client.post("/api/cover-letter/", json={
        "title": "CL", "target_company": "C", "target_role": "R", "job_description": "J",
        "sender_name": "S", "sender_email": "s@s.com"
    })
    assert response.status_code == 200


def test_get_cl(override_deps, mock_cl_repo):
    cid, now = str(ObjectId()), datetime.now()
    mock_cl_repo.get_cover_letter_by_id.return_value = {
        "_id": ObjectId(cid), "title": "C"}
    assert client.get(f"/api/cover-letter/{cid}").status_code == 200

    mock_cl_repo.get_cover_letters_by_user_id.return_value = [{"_id": ObjectId(
    ), "title": "C", "target_company": "C", "target_role": "R", "is_generated": False, "created_at": now, "updated_at": now}]
    assert client.get("/api/cover-letter/user/u1").status_code == 200


def test_cl_crud(override_deps, mock_cl_repo):
    cid = str(ObjectId())
    mock_cl_repo.get_cover_letter_by_id.return_value = {"_id": ObjectId(cid)}
    mock_cl_repo.update_cover_letter.return_value = True
    mock_cl_repo.delete_cover_letter.return_value = True

    assert client.put(
        f"/api/cover-letter/{cid}", json={"title": "N"}).status_code == 200
    assert client.delete(f"/api/cover-letter/{cid}").status_code == 200


def test_cl_ai(override_deps, mock_ai_gen):
    mock_ai_gen.generate_cover_letter.return_value = "AI"
    response = client.post("/api/cover-letter/generate-with-ai", json={
                           "resume_text": "R", "job_description": "J", "company_name": "C", "job_title": "T"})
    assert response.status_code == 200
    assert response.json()["content"] == "AI"


def test_cl_search_stats(override_deps, mock_cl_repo):
    mock_cl_repo.search_cover_letters.return_value, mock_cl_repo.get_cover_letter_statistics.return_value = [
    ], {"total": 5}
    assert client.get(
        "/api/cover-letter/search/u1?query=test").status_code == 200
    assert client.get("/api/cover-letter/statistics/u1").status_code == 200

# === COMPREHENSIVE OPTIMIZER TESTS ===


def test_comp_opt(override_deps, mock_comp_optimizer):
    mock_comp_optimizer.optimize_resume_master.return_value = {"r": "ok"}
    mock_comp_optimizer.analyze_ats_keywords.return_value = {"keywords": []}
    mock_comp_optimizer.extract_hidden_achievements.return_value = {
        "achievements": []}
    mock_comp_optimizer.create_three_versions.return_value = {"versions": []}
    mock_comp_optimizer.iterative_improvement.return_value = {"improved": True}

    assert client.post("/api/comprehensive/optimize/master", json={
                       "target_role": "R", "job_description": "J", "resume_text": "R"}).status_code == 200
    assert client.post("/api/comprehensive/analyze/ats",
                       json={"job_description": "J", "resume_text": "R"}).status_code == 200
    assert client.post("/api/comprehensive/extract/achievements",
                       json={"role_description": "R"}).status_code == 200
    assert client.post("/api/comprehensive/create/three-versions",
                       json={"job_description": "J", "resume_text": "R"}).status_code == 200
    assert client.post("/api/comprehensive/improve/iterative",
                       json={"job_description": "J", "resume_text": "R"}).status_code == 200


def test_comp_opt_getters(override_deps, mock_comp_optimizer):
    mock_comp_optimizer.get_quick_start_workflows.return_value = {
        "5min": "Quick"}
    mock_comp_optimizer.get_pro_tips.return_value = ["Tip"]
    mock_comp_optimizer.get_eu_2025_alignment.return_value = {"ats": []}

    assert client.get("/api/comprehensive/workflows").status_code == 200
    assert client.get("/api/comprehensive/tips").status_code == 200
    assert client.get("/api/comprehensive/eu-alignment").status_code == 200
    assert client.get("/api/comprehensive/skills").status_code == 200
