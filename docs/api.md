# API Documentation

## Authentication

All endpoints (except `/api/users/login` and `/api/users/register`) require JWT authentication.

### Login
```http
POST /api/users/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ...
```

### Refresh Token
```http
POST /api/users/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

---

## Assets

### List Assets
```http
GET /api/assets/
GET /api/assets/?category=laptop
GET /api/assets/?status=available
GET /api/assets/?assigned_to=2
```

### Create Asset
```http
POST /api/assets/
Content-Type: application/json

{
  "name": "MacBook Pro 16\"",
  "category": "laptop",
  "description": "M3 Max chip",
  "serial_number": "FVFXC2ABCD01",
  "manufacturer": "Apple",
  "model": "MacBook Pro 16\" M3 Max",
  "location": "IT Storage Room A"
}
```

### Get Asset
```http
GET /api/assets/{id}
GET /api/assets/tag/{asset_tag}
```

### Update Asset
```http
PATCH /api/assets/{id}
Content-Type: application/json

{
  "location": "Engineering Floor 3",
  "status": "maintenance"
}
```

### Check Out Asset
```http
POST /api/assets/{id}/checkout
Content-Type: application/json

{
  "user_id": 2,
  "notes": "Assigned to new employee"
}
```

### Check In Asset
```http
POST /api/assets/{id}/checkin
Content-Type: application/json

{
  "notes": "Returned in good condition"
}
```

### Get Asset History
```http
GET /api/assets/{id}/history
```

### Export Assets
```http
POST /api/assets/export
Content-Type: application/json

{
  "format": "csv",
  "category": "laptop"
}
```

---

## Search

### Basic Search
```http
GET /api/search/?q=macbook&category=laptop&status=available
```

### AI-Powered Search
```http
POST /api/search/ai
Content-Type: application/json

{
  "query": "show me all laptops assigned to engineering"
}
```

Response includes:
- `assets`: Matching assets
- `total`: Result count
- `query_interpretation`: How the AI parsed the query

---

## QR Codes

### Generate QR Code
```http
GET /api/qr/{asset_id}
```
Returns PNG image.

### Batch QR Codes
```http
GET /api/qr/batch?asset_ids=1,2,3
```
Returns JSON with base64-encoded QR codes.

---

## Users

### List Users (Admin only)
```http
GET /api/users/
```

### Get Current User
```http
GET /api/users/me
```

### Create User (Admin only)
```http
POST /api/users/register
Content-Type: application/json

{
  "email": "new@company.com",
  "username": "newuser",
  "password": "securepassword",
  "full_name": "New User",
  "department": "Engineering",
  "role": "user"
}
```

Roles: `admin`, `user`, `auditor`

---

## Audit Logs

### List Audit Logs (Admin/Auditor only)
```http
GET /api/audit/
GET /api/audit/?entity_type=asset
GET /api/audit/?action=checkout
GET /api/audit/?user_id=1
GET /api/audit/?start_date=2024-01-01T00:00:00
```

### Get Entity Audit Trail
```http
GET /api/audit/entity/asset/1
```

### Get Audit Summary
```http
GET /api/audit/summary?days=30
```

---

## Dashboard

### Get Dashboard Stats
```http
GET /api/assets/dashboard
```

Response:
```json
{
  "total_assets": 15,
  "available_assets": 8,
  "checked_out_assets": 5,
  "maintenance_assets": 1,
  "retired_assets": 1,
  "assets_by_category": {
    "laptop": 5,
    "monitor": 4,
    "keyboard": 2
  },
  "recent_activity": [...]
}
```

---

## Error Responses

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `400`: Bad request
- `401`: Unauthorized
- `403`: Forbidden (insufficient permissions)
- `404`: Not found
- `422`: Validation error
