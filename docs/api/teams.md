# API: команды

Префикс: `/teams`.

---

## `GET /teams/`

Описание: список команд.

**Пример ответа:** `200 OK` — `List[Team]`.

**Код эндпоинта:**

```python
@router.get("/", response_model=List[Team])
def list_teams(session: Session = Depends(get_session)) -> List[Team]:
    return session.exec(select(Team)).all()
```

---

## `GET /teams/{team_id}`

Описание: команда с участниками (`TeamWithMembers`).

**Пример ответа:** `200 OK`

```json
{
  "name": "Core",
  "description": "",
  "project_id": 1,
  "members": []
}
```

**Код эндпоинта:**

```python
@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(team_id: int, session: Session = Depends(get_session)) -> Team:
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members))
    )
    team = session.exec(stmt).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    return team
```

---

## `POST /teams/`

Описание: создать команду (`TeamDefault`).

**Пример запроса:**

```bash
curl -s -X POST http://127.0.0.1:8000/teams/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Core","description":"","project_id":1}'
```

**Пример ответа:** `200 OK`

```json
{"status": 200, "data": {"id": 1, "name": "Core", "description": "", "project_id": 1}}
```

**Код эндпоинта:**

```python
@router.post("/", response_model=TeamCreateResponse)
def create_team(
    payload: TeamDefault, session: Session = Depends(get_session)
) -> TeamCreateResponse:
    team = Team(**payload.model_dump())
    session.add(team)
    session.commit()
    session.refresh(team)
    return {"status": 200, "data": team}
```

---

## `PATCH /teams/{team_id}`

Описание: частичное обновление (`TeamPatch`), ответ — `Team`.

**Код эндпоинта:**

```python
@router.patch("/{team_id}", response_model=Team)
def patch_team(
    team_id: int,
    patch: TeamPatch,
    session: Session = Depends(get_session),
) -> Team:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(team, key, value)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team
```

---

## `DELETE /teams/{team_id}`

Описание: удалить команду и строки `TeamMember`.

**Пример ответа:** `{"ok": true}`

**Код эндпоинта:**

```python
@router.delete("/{team_id}", response_model=OkResponse)
def delete_team(team_id: int, session: Session = Depends(get_session)) -> OkResponse:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Not found")
    for link in session.exec(
        select(TeamMember).where(TeamMember.team_id == team_id)
    ).all():
        session.delete(link)
    session.delete(team)
    session.commit()
    return {"ok": True}
```

---

## `POST /teams/{team_id}/members/{user_id}`

Описание: добавить участника (`TeamMember`).

| Query | Описание |
|-------|----------|
| `member_role` | По умолчанию `member`. |

**Пример запроса:**

```bash
curl -s -X POST "http://127.0.0.1:8000/teams/1/members/2?member_role=lead"
```

**Пример ответа:** `{"ok": true}`

**Код эндпоинта:**

```python
@router.post("/{team_id}/members/{user_id}", response_model=OkResponse)
def add_team_member(
    team_id: int,
    user_id: int,
    session: Session = Depends(get_session),
    member_role: str = Query(default="member"),
) -> OkResponse:
    if session.get(Team, team_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Not found")
    existing = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=400, detail="User is already a member of this team"
        )
    link = TeamMember(
        team_id=team_id,
        user_id=user_id,
        member_role=member_role,
    )
    session.add(link)
    session.commit()
    return {"ok": True}
```

---

## `DELETE /teams/{team_id}/members/{user_id}`

Описание: убрать участника из команды.

**Код эндпоинта:**

```python
@router.delete("/{team_id}/members/{user_id}", response_model=OkResponse)
def remove_team_member(
    team_id: int, user_id: int, session: Session = Depends(get_session)
) -> OkResponse:
    link = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
```
