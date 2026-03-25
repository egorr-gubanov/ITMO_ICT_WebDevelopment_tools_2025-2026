# API: навыки

Префикс: `/skills`. База: `http://127.0.0.1:8000`.

---

## `GET /skills/`

Описание: список всех навыков.

**Пример запроса:**

```bash
curl -s http://127.0.0.1:8000/skills/
```

**Пример ответа:** `200 OK`

```json
[
  {"id": 1, "name": "Python", "description": ""}
]
```

**Код эндпоинта:**

```python
@router.get("/", response_model=List[Skill])
def list_skills(session: Session = Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()
```

---

## `GET /skills/{skill_id}`

Описание: один навык.

| Path | Тип | Описание |
|------|-----|----------|
| `skill_id` | `int` | ID навыка |

**Пример запроса:**

```bash
curl -s http://127.0.0.1:8000/skills/1
```

**Пример ответа:** `200 OK`

```json
{"id": 1, "name": "Python", "description": ""}
```

**Ошибка:** `404` — `{"detail":"Not found"}`.

**Код эндпоинта:**

```python
@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    return skill
```

---

## `POST /skills/`

Описание: создать навык из `SkillDefault`.

**Body (JSON):** `name`, `description` (опционально).

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/skills/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Docker","description":"Containers"}'
```

**Пример ответа:** `200 OK`

```json
{
  "status": 200,
  "data": {"id": 2, "name": "Docker", "description": "Containers"}
}
```

**Код эндпоинта:**

```python
@router.post("/", response_model=SkillCreateResponse)
def create_skill(
    payload: SkillDefault, session: Session = Depends(get_session)
) -> SkillCreateResponse:
    skill = Skill(**payload.model_dump())
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}
```

---

## `PATCH /skills/{skill_id}`

Описание: частичное обновление (`SkillPatch`).

| Path | Описание |
|------|----------|
| `skill_id` | `int` |

**Body:** любое из `name`, `description`.

**Пример запроса:**

```bash
curl -s -X PATCH http://127.0.0.1:8000/skills/2 \
  -H "Content-Type: application/json" \
  -d '{"description":"Docker & Compose"}'
```

**Пример ответа:** `200 OK`

```json
{"id": 2, "name": "Docker", "description": "Docker & Compose"}
```

**Код эндпоинта:**

```python
@router.patch("/{skill_id}", response_model=Skill)
def patch_skill(
    skill_id: int,
    patch: SkillPatch,
    session: Session = Depends(get_session),
) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(skill, key, value)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill
```

---

## `DELETE /skills/{skill_id}`

Описание: удалить навык и связанные `UserSkillLink`.

**Пример запроса:**

```bash
curl -s -X DELETE http://127.0.0.1:8000/skills/2
```

**Пример ответа:** `200 OK`

```json
{"ok": true}
```

**Код эндпоинта:**

```python
@router.delete("/{skill_id}", response_model=OkResponse)
def delete_skill(skill_id: int, session: Session = Depends(get_session)) -> OkResponse:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(UserSkillLink).where(UserSkillLink.skill_id == skill_id)
    ).all():
        session.delete(link)
    session.delete(skill)
    session.commit()
    return {"ok": True}
```
