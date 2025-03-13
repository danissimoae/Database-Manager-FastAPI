from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import pandas as pd
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

# Создаем базу данных SQLite
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение моделей
class SearchSystem(Base):
    __tablename__ = "search_systems"
    search_system_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    sources = relationship("Source", back_populates="search_system")


class Source(Base):
    __tablename__ = "sources"
    source_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    search_system_id = Column(Integer, ForeignKey("search_systems.search_system_id"))
    url = Column(String)
    description = Column(String)
    search_system = relationship("SearchSystem", back_populates="sources")


# Создание таблиц
Base.metadata.create_all(bind=engine)


# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создаем приложение FastAPI
app = FastAPI()

# Подключаем статику
app.mount("/static", StaticFiles(directory="static"), name="static")

# Главная страница
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as file:
        return file.read()


# Загрузка данных при старте
@app.on_event("startup")
def load_data():
    db = SessionLocal()
    try:
        search_systems_df = pd.read_csv("data/Поисковые системы.csv", sep=";", encoding="windows-1251")
        sources_df = pd.read_csv("data/Источники.csv", sep=";", encoding="windows-1251")
        search_systems_df.columns = ["search_system_id", "name", "url"]
        sources_df.columns = ["source_id", "search_system_id", "url", "description"]

        for _, row in search_systems_df.iterrows():
            db.add(SearchSystem(search_system_id=row["search_system_id"], name=row["name"], url=row["url"]))
        db.commit()

        for _, row in sources_df.iterrows():
            db.add(Source(source_id=row["source_id"], search_system_id=row["search_system_id"],
                          url=row["url"], description=row["description"]))
        db.commit()
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
    finally:
        db.close()


# CRUD API
@app.get("/search-systems/")
def get_search_systems(db: Session = Depends(get_db)):
    return db.query(SearchSystem).all()


@app.get("/sources/")
def get_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


# Fetch a specific source by ID with its associated search system information
@app.get("/sources/{source_id}")
def get_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.source_id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    # Return source along with the search system's name
    return {
        "source_id": source.source_id,
        "url": source.url,
        "description": source.description,
        "search_system_name": source.search_system.name  # Include search system's name
    }


@app.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.source_id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")
    db.delete(source)
    db.commit()
    return {"message": "Источник удален"}


@app.get("/sources/search/")
def search_sources(query: str, db: Session = Depends(get_db)):
    results = db.query(Source).filter(Source.description.ilike(f"%{query}%")).all()
    return results


from fastapi import Body

@app.post("/sources/")
def add_source(
    search_system_id: int = Body(...),
    url: str = Body(...),
    description: str = Body(...),
    db: Session = Depends(get_db)
):
    # Првоеряем существует ли поисковая система
    search_system = db.query(SearchSystem).filter(SearchSystem.search_system_id == search_system_id).first()
    if not search_system:
        raise HTTPException(status_code=400, detail="Такой поисковой системы не существует")

    new_source = Source(url=url, description=description, search_system_id=search_system_id)
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


@app.post("/search-systems/")
def add_search_system(name: str, url: str, db: Session = Depends(get_db)):
    new_system = SearchSystem(name=name, url=url)
    db.add(new_system)
    db.commit()
    db.refresh(new_system)
    return new_system

