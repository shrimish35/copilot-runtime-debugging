# Runtime Debugging Lab

This project contains the fixed application. The original failures and challenge
failures were reproduced using FastAPI's TestClient before the fixes were applied.
The snippets below let you reintroduce each failure individually for practice.

## Setup

On Linux or macOS:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows, use `python -m venv venv` and activate with
`venv\Scripts\activate` instead. Open http://127.0.0.1:8000/docs for Swagger UI.
In a second terminal with the virtual environment activated, run `pytest -v`.

## Reproduce and debug

For each exercise, temporarily replace the named function body with its snippet,
invoke the request, and observe the traceback in the server terminal. Restore the
fixed body afterward. Do not change the route decorators or their order: static
employee routes must precede `/employee/{employee_id}`.

1. **TypeError**: In `calculate_bonus`, replace its body with:

   ```python
   salary = "50000"
   bonus = salary * 0.10
   return {"bonus": bonus}
   ```

   Request `GET /employee/bonus`. A string cannot be multiplied by a float;
   use a numeric salary. The fixed response is `{"bonus": 5000.0}`.

2. **KeyError**: In `get_employee`, replace its body with:

   ```python
   return employees[employee_id]
   ```

   Request `GET /employee/999`. Indexing raises `KeyError` for a missing key;
   `get()` instead returns `None` when no default is specified. The fixed
   endpoint returns 404 for a missing employee and 200 for `/employee/101`.

3. **ZeroDivisionError**: In `calculate_average_salary`, replace its body with:

   ```python
   total_salary = 150000
   employee_count = 0
   average = total_salary / employee_count
   return {"average_salary": average}
   ```

   Request `GET /employee/average-salary`. Division by zero is undefined; the
   fixed endpoint rejects non-positive counts with 400. With query parameters
   `total_salary=150000&employee_count=3`, it returns `50000.0`.

4. **ValueError**: In `parse_salary`, replace its body with:

   ```python
   return {"salary": float(value)}
   ```

   Request `GET /employee/salary?value=invalid`. An invalid numeric string
   cannot be converted to a float. The fixed endpoint returns 400 for invalid,
   negative, or non-finite values.

5. **AttributeError**: In `get_employee_field`, replace its body with:

   ```python
   from types import SimpleNamespace

   employee = SimpleNamespace(**employees[employee_id])
   return {"value": getattr(employee, field)}
   ```

   Request `GET /employee/101/fields/missing`. The object has no such
   attribute. The fixed endpoint checks the dictionary and returns 404.

6. **IndexError**: In `get_department`, replace its body with:

   ```python
   return {"department": departments[index]}
   ```

   Request `GET /departments/99`. The index is outside the list. The fixed
   endpoint checks its bounds and returns 404.

7. **ValidationError**: Replace `create_employee` with:

   ```python
   def create_employee(payload: dict):
       return Employee(**payload)
   ```

   Send `POST /employee` with JSON
   `{"name": "Rahul", "age": "invalid", "salary": 50000}`. Manually
   constructing the model raises a Pydantic `ValidationError` inside the
   endpoint. The fixed endpoint declares an `Employee` body, so FastAPI returns
   422 for invalid input before the handler runs.

The unhandled exceptions produce server errors; `TestClient` raises them by
default, exposing their exception types. Restore each fixed implementation before
running the regression suite.

## Copilot debugging prompt

Use this structured prompt for each exercise, filling in the exception, request,
traceback, and function body:

```text
You are an expert Python and FastAPI developer.
Request: <method and URL>
Exception and traceback: <paste here>
Code: <paste the affected function>

Explain the root cause and identify the incorrect statement. Explain why Python
raises this exception, then propose the smallest safe fix and the appropriate
HTTP response. Include corrected code and tests for both valid and invalid
inputs. Explain first; do not modify code until I have reviewed your explanation.
```

For `KeyError`, also ask how dictionary indexing differs from `get()`. For
`ZeroDivisionError`, ask how to handle zero employees. For `ValidationError`,
ask how FastAPI request validation differs from manual model construction.

## Final review prompt

```text
Review my FastAPI application and Pytest tests. Verify the TypeError, KeyError,
and ZeroDivisionError fixes; review exception handling, HTTP status codes and
test coverage; identify remaining runtime risks and suggest Python and FastAPI
best practices. Explain any proposed changes before modifying code.
```

The fixed application returns 400 for invalid counts and salary query values,
404 for missing employees, fields and departments, and 422 for invalid request
bodies. Validation error details omit raw inputs to avoid serializing non-finite
numbers. The employee POST validates and echoes data; it does not persist it.
For production, consider decimal arithmetic for money, additional employee
constraints, persistent storage, and pinned or locked dependency versions.