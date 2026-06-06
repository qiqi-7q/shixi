from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.plugins.employee_plugin import schemas, services

router = APIRouter()


@router.post("/", response_model=schemas.Employee)
def create_employee(data: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return services.create_employee(db=db, data=data)


@router.get("/", response_model=list[schemas.Employee])
def get_employees_list(
    skip: int = 0,
    limit: int = 100,
    name: str = Query(None, description="按姓名筛选（模糊匹配）"),
    company: str = Query(None, description="按公司筛选（模糊匹配）"),
    db: Session = Depends(get_db)
):
    return services.get_employees(db, skip=skip, limit=limit, name=name, company=company)


@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return services.get_employee(db, employee_id=employee_id)


@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int, data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    return services.update_employee(db, employee_id=employee_id, data=data)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    return services.delete_employee(db, employee_id=employee_id)
