
# 🎓 Student Management API

A secure **FastAPI + MongoDB** based Student Management System with per-user secret key authentication using JWT.


<img width="1561" height="783" alt="image" src="https://github.com/user-attachments/assets/0d2b9f9a-717c-4547-8a72-ae8fecd84f02" />

---

## 🚀 Features

- 🔐 **Per-user secret key** for JWT generation
- 👨‍🎓 Full CRUD operations on students
- 🛡️ Token-based authentication with hashed passwords
- 📦 MongoDB NoSQL storage

---

## 📦 Requirements

```bash
pip install fastapi uvicorn pymongo python-jose passlib[bcrypt]
```

---

## ⚙️ Setup Instructions

1. **Run MongoDB locally** (`mongodb://localhost:27017`)
2. **Start the server**:

```bash
uvicorn main:app --reload
```

---

## 🔐 Authentication Flow

### 1. **Register**
- Generates a user-specific secret key (`secrets.token_hex(32)`)
- Stores in MongoDB

### 2. **Login**
- Validates credentials
- Fetches user’s secret key from DB
- Creates JWT signed with that key

### 3. **Token Verification**
- Extracts `sub` (username) from token
- Fetches the same user's `secret_key`
- Verifies token with that

---

## 🧪 Example API Usage

### 🔓 Public

#### `POST /register`
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secure123"
}
```

#### `POST /login`
Form data:
```
username=alice
password=secure123
```

Returns:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

---

### 🔐 Protected Routes (Require Bearer Token)

#### `GET /students`
#### `POST /students`
#### `GET /students/{roll_no}`
#### `PUT /students/{roll_no}`
#### `DELETE /students/{roll_no}`

> Use JWT token from login in `Authorization` header:
```
Authorization: Bearer <token>
```

---

## 📁 MongoDB Collections

- **users**
  - `username`, `email`, `password`, `secret_key`
- **students**
  - `roll_no`, `name`, `branch`, `marks`

---

## 🧠 Security Notes

- Passwords hashed with `bcrypt`
- Unique secret keys prevent shared token compromise
- JWT tokens expire in 30 minutes by default

---

## 👨‍💻 Author

**Konduri Varun**
