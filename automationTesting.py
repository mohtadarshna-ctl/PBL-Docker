import os
import sys
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def run_tests():
    # 1. Root endpoint
    resp = requests.get(f"{BASE_URL}/", timeout=5)
    assert resp.status_code == 200, f"GET / failed with {resp.status_code}"
    root_data = resp.json()
    assert root_data.get("status") == "running", f"Unexpected root payload: {root_data}"
    print("PASS: GET /")

    # 2. Health check endpoint
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    assert resp.status_code == 200, f"GET /health failed with {resp.status_code}"
    assert resp.json() == {"status": "healthy"}, f"Unexpected health payload: {resp.json()}"
    print("PASS: GET /health")

    # 3. List all students
    resp = requests.get(f"{BASE_URL}/students", timeout=5)
    assert resp.status_code == 200, f"GET /students failed with {resp.status_code}"
    initial_students = resp.json()
    assert isinstance(initial_students, list) and len(initial_students) >= 1
    print("PASS: GET /students")

    # 4. Create a new student
    new_student_payload = {
        "name": "Kabir Nair",
        "course": "DevOps Engineering",
        "semester": 6,
    }
    resp = requests.post(f"{BASE_URL}/students", json=new_student_payload, timeout=5)
    assert resp.status_code == 201, f"POST /students failed with {resp.status_code}: {resp.text}"
    created = resp.json()
    created_id = created["id"]
    assert created["name"] == new_student_payload["name"]
    assert created["course"] == new_student_payload["course"]
    assert created["semester"] == new_student_payload["semester"]
    print(f"PASS: POST /students (id={created_id})")

    # 5. Get the created student by ID
    resp = requests.get(f"{BASE_URL}/students/{created_id}", timeout=5)
    assert resp.status_code == 200, f"GET /students/{created_id} failed with {resp.status_code}"
    assert resp.json()["name"] == "Kabir Nair"
    print(f"PASS: GET /students/{created_id}")

    # 6. Filter students by course
    resp = requests.get(f"{BASE_URL}/students", params={"course": "DevOps Engineering"}, timeout=5)
    assert resp.status_code == 200, f"GET /students?course=... failed with {resp.status_code}"
    filtered = resp.json()
    assert any(s["id"] == created_id for s in filtered), "Created student missing from course filter"
    print("PASS: GET /students?course=DevOps Engineering")

    # 7. Update the created student
    update_payload = {"course": "Containerization & CI/CD", "semester": 7}
    resp = requests.put(f"{BASE_URL}/students/{created_id}", json=update_payload, timeout=5)
    assert resp.status_code == 200, f"PUT /students/{created_id} failed with {resp.status_code}"
    updated = resp.json()
    assert updated["course"] == "Containerization & CI/CD"
    assert updated["semester"] == 7
    print(f"PASS: PUT /students/{created_id}")

    # 8. Delete the created student
    resp = requests.delete(f"{BASE_URL}/students/{created_id}", timeout=5)
    assert resp.status_code == 200, f"DELETE /students/{created_id} failed with {resp.status_code}"
    assert resp.json().get("deleted") is True
    print(f"PASS: DELETE /students/{created_id}")

    # 9. Verify deleted student returns 404
    resp = requests.get(f"{BASE_URL}/students/{created_id}", timeout=5)
    assert resp.status_code == 404, f"Expected 404 after delete, got {resp.status_code}"
    print(f"PASS: GET /students/{created_id} returns 404 after deletion")

    print("All automated route tests passed.")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as exc:
        print(f"TEST FAILURE: {exc}", file=sys.stderr)
        sys.exit(1)
