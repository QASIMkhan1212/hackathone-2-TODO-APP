# SQLModel Relationships

## One-to-Many Relationship

### Model Definition

```python
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationship: One team has many members
    members: list["User"] = Relationship(back_populates="team")


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    # Foreign key
    team_id: int | None = Field(default=None, foreign_key="team.id")

    # Relationship: Each user belongs to one team
    team: Team | None = Relationship(back_populates="members")
```

### Creating Related Objects

```python
from sqlmodel import Session

def create_team_with_members(session: Session):
    # Create team
    team = Team(name="Engineering")
    session.add(team)
    session.commit()
    session.refresh(team)

    # Create members
    user1 = User(name="Alice", email="alice@example.com", team_id=team.id)
    user2 = User(name="Bob", email="bob@example.com", team_id=team.id)
    session.add(user1)
    session.add(user2)
    session.commit()

    return team

# Alternative: Create all at once
def create_team_with_members_v2(session: Session):
    team = Team(
        name="Engineering",
        members=[
            User(name="Alice", email="alice@example.com"),
            User(name="Bob", email="bob@example.com"),
        ],
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    return team
```

### Querying with Relationships

```python
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

# Get team with members (eager loading)
def get_team_with_members(session: Session, team_id: int) -> Team | None:
    statement = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members))
    )
    return session.exec(statement).first()

# Get user with team
def get_user_with_team(session: Session, user_id: int) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.team))
    )
    return session.exec(statement).first()

# Query users by team
def get_users_by_team(session: Session, team_name: str) -> list[User]:
    statement = (
        select(User)
        .join(Team)
        .where(Team.name == team_name)
    )
    return session.exec(statement).all()
```

---

## Many-to-Many Relationship

### Model Definition with Link Table

```python
from sqlmodel import SQLModel, Field, Relationship

# Link table (association table)
class ProjectUserLink(SQLModel, table=True):
    project_id: int | None = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: int | None = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    role: str = Field(default="member")  # Extra data on relationship


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    # Many-to-many relationship
    users: list["User"] = Relationship(
        back_populates="projects",
        link_model=ProjectUserLink,
    )


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    # Many-to-many relationship
    projects: list[Project] = Relationship(
        back_populates="users",
        link_model=ProjectUserLink,
    )
```

### Working with Many-to-Many

```python
def add_user_to_project(
    session: Session,
    user_id: int,
    project_id: int,
    role: str = "member",
):
    # Create link directly
    link = ProjectUserLink(
        user_id=user_id,
        project_id=project_id,
        role=role,
    )
    session.add(link)
    session.commit()

def get_project_users(session: Session, project_id: int) -> list[User]:
    statement = (
        select(User)
        .join(ProjectUserLink)
        .where(ProjectUserLink.project_id == project_id)
    )
    return session.exec(statement).all()

def get_user_projects(session: Session, user_id: int) -> list[Project]:
    statement = (
        select(Project)
        .join(ProjectUserLink)
        .where(ProjectUserLink.user_id == user_id)
    )
    return session.exec(statement).all()

def remove_user_from_project(
    session: Session,
    user_id: int,
    project_id: int,
):
    statement = select(ProjectUserLink).where(
        ProjectUserLink.user_id == user_id,
        ProjectUserLink.project_id == project_id,
    )
    link = session.exec(statement).first()
    if link:
        session.delete(link)
        session.commit()
```

---

## One-to-One Relationship

### Model Definition

```python
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    # One-to-one: User has one profile
    profile: "Profile" | None = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False},
    )


class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bio: str | None = None
    avatar_url: str | None = None

    # Foreign key (unique ensures one-to-one)
    user_id: int = Field(foreign_key="user.id", unique=True)

    # Back reference
    user: User = Relationship(back_populates="profile")
```

### Working with One-to-One

```python
def create_user_with_profile(session: Session):
    user = User(name="John", email="john@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)

    profile = Profile(
        user_id=user.id,
        bio="Software developer",
        avatar_url="https://example.com/avatar.jpg",
    )
    session.add(profile)
    session.commit()

    return user

def get_user_with_profile(session: Session, user_id: int) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.profile))
    )
    return session.exec(statement).first()
```

---

## Self-Referential Relationship

### Model Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Self-referential foreign key
    parent_id: int | None = Field(default=None, foreign_key="category.id")

    # Parent relationship
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )

    # Children relationship
    children: list["Category"] = Relationship(back_populates="parent")
```

### Working with Hierarchies

```python
def create_category_tree(session: Session):
    # Root category
    root = Category(name="Electronics")
    session.add(root)
    session.commit()
    session.refresh(root)

    # Child categories
    phones = Category(name="Phones", parent_id=root.id)
    laptops = Category(name="Laptops", parent_id=root.id)
    session.add(phones)
    session.add(laptops)
    session.commit()

    # Grandchild
    iphones = Category(name="iPhones", parent_id=phones.id)
    session.add(iphones)
    session.commit()

    return root

def get_category_with_children(
    session: Session,
    category_id: int,
) -> Category | None:
    statement = (
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.children))
    )
    return session.exec(statement).first()

def get_all_descendants(session: Session, category_id: int) -> list[Category]:
    """Recursively get all descendants."""
    result = []
    category = get_category_with_children(session, category_id)
    if category:
        for child in category.children:
            result.append(child)
            result.extend(get_all_descendants(session, child.id))
    return result
```

---

## Cascade Operations

### Delete Cascade

```python
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    members: list["User"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="members")
```

### Cascade Options

| Option | Description |
|--------|-------------|
| `save-update` | Cascade add to session |
| `merge` | Cascade merge operations |
| `delete` | Cascade delete |
| `delete-orphan` | Delete when removed from collection |
| `all` | All cascades except delete-orphan |
| `all, delete-orphan` | All cascades including orphan deletion |

---

## Loading Strategies

### Eager Loading (selectinload)

```python
from sqlalchemy.orm import selectinload

# Load related objects in separate SELECT
statement = (
    select(Team)
    .options(selectinload(Team.members))
)
```

### Joined Loading (joinedload)

```python
from sqlalchemy.orm import joinedload

# Load related objects in same query via JOIN
statement = (
    select(User)
    .options(joinedload(User.team))
)
```

### Subquery Loading (subqueryload)

```python
from sqlalchemy.orm import subqueryload

# Load via subquery
statement = (
    select(Team)
    .options(subqueryload(Team.members))
)
```

### When to Use Each

| Strategy | Best For |
|----------|----------|
| `selectinload` | Collections (one-to-many), many small objects |
| `joinedload` | Single objects (many-to-one), eager loading one item |
| `subqueryload` | Large collections with complex filters |
