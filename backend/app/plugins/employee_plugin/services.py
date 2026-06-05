from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.plugins.employee_plugin import models, schemas


def create_employee(db: Session, data: schemas.EmployeeCreate):
    db_employee = models.Employee(**data.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employees(db: Session, skip: int = 0, limit: int = 100, name: str = None, company: str = None):
    query = db.query(models.Employee)
    if name:
        query = query.filter(models.Employee.name.like(f"%{name}%"))
    if company:
        query = query.filter(models.Employee.third_party_company.like(f"%{company}%"))
    return query.offset(skip).limit(limit).all()


def get_employee(db: Session, employee_id: int):
    item = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="员工不存在")
    return item


def update_employee(db: Session, employee_id: int, data: schemas.EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    db.delete(db_employee)
    db.commit()
    return {"msg": "删除成功"}
