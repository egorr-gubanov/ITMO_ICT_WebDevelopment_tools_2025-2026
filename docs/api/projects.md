# API: проекты

Префикс: `/projects`.

---

## `GET /projects/`

Описание: список всех проектов.

**Пример запроса:**

```bash
curl -s http://127.0.0.1:8000/projects/
```

**Пример ответа:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Team finder",
    "description": "MVP",
    "required_skills": "Python, SQL",
    "status": "open",
    "owner_id": null
  }
]
```

**Код эндпоинта:**

```python
@router.get("/", response_model=List[Project])
def list_projects(session: Session = Depends(get_session)) -> List[Project]:
    return session.exec(select(Project)).all()
```

---

## `GET /projects/search`

Описание: фильтр проектов по полю `status`.

| Query | Описание |
|-------|----------|
| `status` | Опционально, например `open`. |

**Пример запроса:**

```bash
curl -s "http://127.0.0.1:8000/projects/search?status=open"
```

**Пример ответа:** `200 OK` — массив `Project`.

**Код эндпоинта:**

```python
@router.get("/search", response_model=List[Project])
def search_projects(
    session: Session = Depends(get_session),
    status: Optional[str] = Query(default=None),
) -> List[Project]:
    stmt = select(Project)
    if status is not None:
        stmt = stmt.where(Project.status == status)
    return list(session.exec(stmt).all())
```

---

## `GET /projects/{project_id}`

Описание: проект с подгруженными командами (`ProjectWithTeams`).

**Пример запроса:**

```bash
curl -s http://127.0.0.1:8000/projects/1
```

**Пример ответа:** `200 OK`

```json
{
  "title": "Team finder",
  "description": "MVP",
  "required_skills": "Python, SQL",
  "status": "open",
  "owner_id": null,
  "teams": []
}
```

**Код эндпоинта:**

```python
@router.get("/{project_id}", response_model=ProjectWithTeams)
def get_project(
    project_id: int, session: Session = Depends(get_session)
) -> Project:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.teams))
    )
    project = session.exec(stmt).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    return project
```

---

## `POST /projects/`

Описание: создать проект (`ProjectDefault`).

**Body:** `title`, `description`, `required_skills`, `status`, `owner_id` (поля по модели).

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"title":"New app","description":"desc","required_skills":"","status":"open","owner_id":null}'
```

**Пример ответа:** `200 OK`

```json
{
  "status": 200,
  "data": {
    "id": 1,
    "title": "New app",
    "description": "desc",
    "required_skills": "",
    "status": "open",
    "owner_id": null
  }
}
```

**Код эндпоинта:**

```python
@router.post("/", response_model=ProjectCreateResponse)
def create_project(
    payload: ProjectDefault, session: Session = Depends(get_session)
) -> ProjectCreateResponse:
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return {"status": 200, "data": project}
```

---

## `PATCH /projects/{project_id}`

Описание: частичное обновление (`ProjectPatch`), ответ — `ProjectDefault`.

**Пример запроса:**

```bash
curl -s -X PATCH http://127.0.0.1:8000/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"closed"}'
```

**Пример ответа:** `200 OK`

```json
{
  "title": "New app",
  "description": "desc",
  "required_skills": "",
  "status": "closed",
  "owner_id": null
}
```

**Код эндпоинта:**

```python
@router.patch("/{project_id}", response_model=ProjectDefault)
def patch_project(
    project_id: int,
    patch: ProjectPatch,
    session: Session = Depends(get_session),
) -> ProjectDefault:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return ProjectDefault.model_validate(project)
```

---

## `DELETE /projects/{project_id}`

Описание: удалить проект, сначала `TeamMember` и `Team`, привязанные к проекту.

**Пример ответа:** `200 OK`

```json
{"ok": true}
```

**Код эндпоинта:**

```python
@router.delete("/{project_id}", response_model=OkResponse)
def delete_project(
    project_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Not found")
    teams = session.exec(
        select(Team).where(Team.project_id == project_id)
    ).all()
    for team in teams:
        for link in session.exec(
            select(TeamMember).where(TeamMember.team_id == team.id)
        ).all():
            session.delete(link)
        session.delete(team)
    session.delete(project)
    session.commit()
    return {"ok": True}
```
