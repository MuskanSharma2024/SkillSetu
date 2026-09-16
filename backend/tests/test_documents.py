import io
import pytest

def test_upload_and_download_resume(client, student_auth):
    """Test valid resume upload, storage, metadata tracking, and download."""
    # Create fake PDF file in memory
    fake_pdf_content = b"%PDF-1.4 Mock resume content for Aarav Sharma SkillSetu"
    file_tuple = ("sample_resume.pdf", io.BytesIO(fake_pdf_content), "application/pdf")

    upload_res = client.post(
        "/api/documents/upload",
        files={"file": file_tuple},
        data={"document_type": "resume"},
        headers=student_auth["headers"]
    )
    assert upload_res.status_code == 201, upload_res.text
    data = upload_res.json()
    assert data["original_filename"] == "sample_resume.pdf"
    assert data["document_type"] == "resume"
    assert "download_url" in data
    doc_id = data["id"]

    # Verify student profile resume_url was updated
    stu_profile = client.get("/api/students/profile", headers=student_auth["headers"]).json()
    assert stu_profile["resume_url"] == f"/api/documents/{doc_id}/download"

    # Download document
    download_res = client.get(f"/api/documents/{doc_id}/download", headers=student_auth["headers"])
    assert download_res.status_code == 200
    assert download_res.content == fake_pdf_content

def test_disallowed_file_extension(client, student_auth):
    """Test that malicious or disallowed file extensions are rejected."""
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
    file_tuple = ("malicious_script.exe", io.BytesIO(fake_exe), "application/x-msdownload")

    res = client.post(
        "/api/documents/upload",
        files={"file": file_tuple},
        data={"document_type": "resume"},
        headers=student_auth["headers"]
    )
    assert res.status_code == 400
    assert "not allowed" in res.json()["detail"].lower()
