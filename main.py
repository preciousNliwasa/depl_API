from fastapi import FastAPI,Depends,Form,Response,status
from sqlalchemy.orm import Session
from typing import Optional
from typing import List
from pydantic import BaseModel
import uvicorn

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.context import CryptContext

pwd_co = CryptContext(schemes = ['bcrypt'],deprecated = 'auto')

class Hashed():
    def cryp(password:str):
        hashed = pwd_co.hash(password)
        return hashed
    
    def verify(password:str,enc:str):
        verified = pwd_co.verify(password,enc)
        return verified 

engine = create_engine('sqlite:///./saharaProduct.db',connect_args = {"check_same_thread":False})

Sessionlocal = sessionmaker(autocommit = False,autoflush = False,bind = engine)
Base = declarative_base()

app = FastAPI(title = 'Product Management API BY MBANLI')

def get_db():
    db = Sessionlocal()
    
    try:
        yield db
    finally:
        db.close()
        
from sqlalchemy import Column,Integer,String

class ProductD(Base):
    __tablename__ = 'product'
    
    id = Column(Integer,primary_key = True,index = True)
    Product = Column(String)
    Type = Column(String)
    Price = Column(Integer)
    Quantity = Column(Integer)
    Date_arrived = Column(String)
    Expiry_date = Column(String)
    Manufactured_date = Column(String)
    Where_bought = Column(String)
    
class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer,primary_key = True,index = True)
    User_name = Column(String)
    Email = Column(String)
    Password = Column(String)

Base.metadata.create_all(bind = engine)


class UserM(BaseModel):
    User_name:str
    Email:str
    class Config():
        orm_mode = True


@app.post('/product',status_code = 201,tags = ['Product'])
async def enter_product(Product:str = Form(...),Type:str = Form(...),Price:int = Form(...),Quantity:int = Form(...),Date_arrived:str = Form(...),Expiry_date:Optional[str] = Form(...),Manufactured_date:Optional[str] = Form(...),Where_bought:str = Form(...),db : Session = Depends(get_db)):
    
    new_product = ProductD(Product = Product,Type = Type,Price = Price,Quantity = Quantity,Date_arrived = Date_arrived,Expiry_date = Expiry_date,Manufactured_date = Manufactured_date,Where_bought = Where_bought )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get('/product',tags = ['Product'])
async def products_list(db : Session = Depends(get_db)):
    products = db.query(ProductD).all()
    return products

@app.get('/product/{id}',status_code = 200,tags = ['Product'])
async def specific_product_details(id:int,response:Response,db : Session = Depends(get_db)):
    product = db.query(ProductD).filter(ProductD.id == id).first()
    
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail':f"id {id} not available"}
    return product

@app.put('/product/{id}',status_code = 202,tags = ['Product'])
async def update_product_details(id:int,response:Response,Product:str = Form(...),Type:str = Form(...),Price:int = Form(...),Quantity:int = Form(...),Date_arrived:str = Form(...),Expiry_date:Optional[str] = Form(...),Manufactured_date:Optional[str] = Form(...),Where_bought:str = Form(...),db : Session = Depends(get_db)):
    product = db.query(ProductD).filter(ProductD.id == id)
    
    if not product.first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail':f"id {id} not available to update"}
        
    product.update(dict(Product = Product,Type = Type,Price = Price,Quantity = Quantity,Date_arrived = Date_arrived,Expiry_date = Expiry_date,Manufactured_date = Manufactured_date,Where_bought = Where_bought))
    db.commit()
    return 'updated'

@app.delete('/product/{id}',status_code = 204,tags = ['Product'])
async def delete_product(id:int,db : Session = Depends(get_db)):
    db.query(ProductD).filter(ProductD.id == id).delete(synchronize_session = False)
    db.commit()
    
    return "Row removed"

@app.post('/user',status_code = 201,tags = ['User'],response_model = UserM)
async def create_customer(User_name:str = Form(...),Email:str = Form(...),Password:str = Form(...),db : Session = Depends(get_db)):
    
    new_user = Users(User_name = User_name,Email = Email,Password = Hashed.cryp(Password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user',tags = ['User'],response_model = List[UserM])
async def customer_list(db : Session = Depends(get_db)):
    customers = db.query(Users).all()
    return customers

@app.put('/user/{id}',status_code = 202,tags = ['User'])
async def update_customer_details(id:int,response:Response,User_name:str = Form(...),Email:str = Form(...),Password:str = Form(...),db : Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == id)
    
    if not user.first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail':f"id {id} not available to update"}
        
    user.update(dict(User_name = User_name,Email = Email,Password = Hashed.cryp(Password)))
    db.commit()
    return 'updated'

@app.delete('/user/{id}',status_code = 204,tags = ['User'])
async def delete_customer(id:int,db : Session = Depends(get_db)):
    db.query(Users).filter(Users.id == id).delete(synchronize_session = False)
    db.commit()
    
    return "Row removed"

@app.post('/Confirm',tags = ['Authenticate'])
async def confirm_user(response:Response,Email:str = Form(...),Password:str = Form(...),db : Session = Depends(get_db)):
    user = db.query(Users).filter(Users.Email == Email).first()
    
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail':f"{Email} not available"}
    
    if not Hashed.verify(Password,user.Password):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail':f"{Password} not available"}
    
    
    return user

if __name__ == '__main__':
    uvicorn.run(app,host = '127.0.0.1',port = 8000)