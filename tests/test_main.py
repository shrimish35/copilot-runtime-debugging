import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_calculate_bonus():
    response = client.get("/employee/bonus")
    assert response.status_code == 200
    assert response.json()["bonus"] == 5000.0


def test_get_existing_employee():
    response = client.get("/employee/101")
    assert response.status_code == 200
    assert response.json() == {"name": "Rahul", "department": "IT"}


def test_get_missing_employee():
    response = client.get("/employee/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee 999 not found"


def test_average_salary():
    response = client.get(
        "/employee/average-salary", params={"total_salary": 150000, "employee_count": 3}
    )
    assert response.status_code == 200
    assert response.json()["average_salary"] == 50000.0


@pytest.mark.parametrize("count", [0, -1])
def test_invalid_employee_count(count):
    response = client.get("/employee/average-salary", params={"employee_count": count})
    assert response.status_code == 400
    assert response.json()["detail"] == "Employee count must be greater than zero"


@pytest.mark.parametrize("total_salary", ["nan", "inf", "-1", "1e309"])
def test_invalid_total_salary(total_salary):
    response = client.get("/employee/average-salary", params={"total_salary": total_salary})
    assert response.status_code == 400
    assert response.json()["detail"] == "Total salary must be a non-negative number"


def test_valid_salary():
    response = client.get("/employee/salary", params={"value": "50000.5"})
    assert response.status_code == 200
    assert response.json() == {"salary": 50000.5}


@pytest.mark.parametrize("value", ["invalid", "-1", "nan", "inf"])
def test_invalid_salary(value):
    response = client.get("/employee/salary", params={"value": value})
    assert response.status_code == 400
    assert response.json()["detail"] == "Salary must be a non-negative number"


def test_existing_employee_field():
    response = client.get("/employee/101/fields/department")
    assert response.status_code == 200
    assert response.json() == {"value": "IT"}


def test_missing_employee_field():
    response = client.get("/employee/101/fields/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee field missing not found"


def test_field_of_missing_employee():
    response = client.get("/employee/999/fields/name")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee 999 not found"


def test_existing_department():
    response = client.get("/departments/0")
    assert response.status_code == 200
    assert response.json() == {"department": "IT"}


@pytest.mark.parametrize("index", [-1, 2, 99])
def test_missing_department(index):
    response = client.get(f"/departments/{index}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Department not found"


def test_valid_employee_payload():
    employee = {"name": "Rahul", "age": 30, "salary": 50000}
    response = client.post("/employee", json=employee)
    assert response.status_code == 200
    assert response.json() == employee


def test_invalid_employee_payload():
    response = client.post(
        "/employee", json={"name": "Rahul", "age": "invalid", "salary": 50000}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "age"]


@pytest.mark.parametrize("salary", ["-1", "1e309"])
def test_invalid_employee_salary(salary):
    response = client.post(
        "/employee",
        content=f'{{"name":"Rahul","age":30,"salary":{salary}}}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "salary"]