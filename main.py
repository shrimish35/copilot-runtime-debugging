from math import isfinite

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="GitHub Copilot Runtime Debugging Lab")


@app.exception_handler(RequestValidationError)
def handle_validation_error(request, exc: RequestValidationError):
    errors = [{key: value for key, value in error.items() if key != "input"} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


class Employee(BaseModel):
    name: str
    age: int
    salary: float = Field(ge=0, allow_inf_nan=False)


employees = {
    101: {"name": "Rahul", "department": "IT"},
    102: {"name": "Priya", "department": "HR"},
}
departments = ["IT", "HR"]


@app.get("/employee/bonus")
def calculate_bonus():
    salary = 50000.0
    bonus = salary * 0.10
    return {"bonus": bonus}


@app.get("/employee/average-salary")
def calculate_average_salary(total_salary: float = 150000, employee_count: int = 3):
    if employee_count <= 0:
        raise HTTPException(status_code=400, detail="Employee count must be greater than zero")
    if not isfinite(total_salary) or total_salary < 0:
        raise HTTPException(status_code=400, detail="Total salary must be a non-negative number")
    average = total_salary / employee_count
    return {"average_salary": average}


@app.get("/employee/salary")
def parse_salary(value: str):
    try:
        salary = float(value)
    except ValueError:
        raise HTTPException(status_code=400, detail="Salary must be a non-negative number")
    if not isfinite(salary) or salary < 0:
        raise HTTPException(status_code=400, detail="Salary must be a non-negative number")
    return {"salary": salary}


@app.get("/departments/{index}")
def get_department(index: int):
    if index < 0 or index >= len(departments):
        raise HTTPException(status_code=404, detail="Department not found")
    return {"department": departments[index]}


@app.post("/employee")
def create_employee(employee: Employee):
    return employee


@app.get("/employee/{employee_id}/fields/{field}")
def get_employee_field(employee_id: int, field: str):
    employee = get_employee(employee_id)
    if field not in employee:
        raise HTTPException(status_code=404, detail=f"Employee field {field} not found")
    return {"value": employee[field]}


@app.get("/employee/{employee_id}")
def get_employee(employee_id: int):
    employee = employees.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return employee


@app.get("/")
def home():
    return {"message": "Runtime Debugging Lab"}