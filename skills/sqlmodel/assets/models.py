"""SQLModel models template with common patterns."""

from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# =============================================================================
# Base Models (Mixins)
# =============================================================================


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# User Model Example
# =============================================================================


class UserBase(SQLModel):
    """User base schema with shared fields."""
    name: str = Field(min_length=1, max_length=100, index=True)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User database model."""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: list["Post"] = Relationship(back_populates="author")
    profile: "Profile" | None = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False},
    )


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Schema for reading a user (API response)."""
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    """Schema for updating a user. All fields optional."""
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


# =============================================================================
# Profile Model (One-to-One with User)
# =============================================================================


class ProfileBase(SQLModel):
    """Profile base schema."""
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    website: str | None = None


class Profile(ProfileBase, table=True):
    """Profile database model (one-to-one with User)."""
    __tablename__ = "profiles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)

    # Relationship
    user: User = Relationship(back_populates="profile")


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    pass


class ProfileRead(ProfileBase):
    """Schema for reading a profile."""
    id: int
    user_id: int


class ProfileUpdate(SQLModel):
    """Schema for updating a profile."""
    bio: str | None = None
    avatar_url: str | None = None
    website: str | None = None


# =============================================================================
# Post Model (One-to-Many with User, Many-to-Many with Tag)
# =============================================================================


class PostTagLink(SQLModel, table=True):
    """Link table for Post-Tag many-to-many relationship."""
    __tablename__ = "post_tags"

    post_id: int | None = Field(
        default=None, foreign_key="posts.id", primary_key=True
    )
    tag_id: int | None = Field(
        default=None, foreign_key="tags.id", primary_key=True
    )


class PostBase(SQLModel):
    """Post base schema."""
    title: str = Field(min_length=1, max_length=200)
    content: str
    published: bool = Field(default=False)


class Post(PostBase, table=True):
    """Post database model."""
    __tablename__ = "posts"

    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    author: User = Relationship(back_populates="posts")
    tags: list["Tag"] = Relationship(
        back_populates="posts",
        link_model=PostTagLink,
    )


class PostCreate(PostBase):
    """Schema for creating a post."""
    tag_ids: list[int] = []


class PostRead(PostBase):
    """Schema for reading a post."""
    id: int
    author_id: int
    created_at: datetime


class PostReadWithAuthor(PostRead):
    """Schema for reading a post with author details."""
    author: UserRead


class PostUpdate(SQLModel):
    """Schema for updating a post."""
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    tag_ids: list[int] | None = None


# =============================================================================
# Tag Model (Many-to-Many with Post)
# =============================================================================


class TagBase(SQLModel):
    """Tag base schema."""
    name: str = Field(unique=True, index=True)


class Tag(TagBase, table=True):
    """Tag database model."""
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)

    # Relationship
    posts: list[Post] = Relationship(
        back_populates="tags",
        link_model=PostTagLink,
    )


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagRead(TagBase):
    """Schema for reading a tag."""
    id: int


# =============================================================================
# Category Model (Self-Referential)
# =============================================================================


class CategoryBase(SQLModel):
    """Category base schema."""
    name: str = Field(index=True)
    description: str | None = None


class Category(CategoryBase, table=True):
    """Category with self-referential parent-child relationship."""
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    parent_id: int | None = Field(default=None, foreign_key="categories.id")

    # Self-referential relationships
    parent: "Category" | None = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: list["Category"] = Relationship(back_populates="parent")


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    parent_id: int | None = None


class CategoryRead(CategoryBase):
    """Schema for reading a category."""
    id: int
    parent_id: int | None


class CategoryReadWithChildren(CategoryRead):
    """Schema for reading a category with children."""
    children: list["CategoryRead"] = []
