# E-commerce Assignment — Django Backend

A Django REST Framework rewrite of the backend for the fullstack e-commerce
assignment (login/signup, 4 products, cart, address, COD checkout). This is
a drop-in alternative to the Node/Express + Supabase backend — same React
frontend can point at this instead by changing the API base URL.

## Stack
- Django 6 + Django REST Framework
- Token authentication (`rest_framework.authtoken`)
- SQLite for local dev, Postgres via `DATABASE_URL` env var in production
- `django-cors-headers` for the React frontend to call the API cross-origin

## Endpoints

| Method | Endpoint            | Auth required | Description                          |
|--------|---------------------|----------------|--------------------------------------|
| POST   | `/api/signup/`       | No            | `{username, email, password}` → creates user, returns token |
| POST   | `/api/login/`        | No            | `{username, password}` → returns token |
| GET    | `/api/products/`     | No            | List all products |
| POST   | `/api/checkout/`     | Yes (Token)   | Places a COD order — body includes address + `items: [{product_id, quantity}]` |
| GET    | `/api/orders/`       | Yes (Token)   | List the logged-in user's past orders |

Auth header format once you have a token: `Authorization: Token <token>`

## Local setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products   # adds the 4 sample products
python manage.py runserver
```

API will be at `http://127.0.0.1:8000/api/`.

## Example: end-to-end curl test

```bash
# Signup
curl -X POST http://127.0.0.1:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tushar1","email":"t@example.com","password":"testpass123"}'

# Login (grab the token from the response)
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tushar1","password":"testpass123"}'

# Products
curl http://127.0.0.1:8000/api/products/

# Checkout (replace TOKEN)
curl -X POST http://127.0.0.1:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token TOKEN" \
  -d '{
    "full_name": "Tushar Aeran",
    "phone": "9999999999",
    "address_line": "123 Test Street",
    "city": "Ludhiana",
    "state": "Punjab",
    "pincode": "141001",
    "items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]
  }'
```

## Deploying (e.g. Render, same as the Node backend)

1. Push this folder to a GitHub repo.
2. On Render: New → Web Service → connect the repo.
   - Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py seed_products`
   - Start command: `gunicorn config.wsgi`
3. Add environment variables:
   - `SECRET_KEY` — any random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — your Render domain, e.g. `your-app.onrender.com`
   - `DATABASE_URL` — if using Render's free Postgres (or Supabase's Postgres
     connection string — same DB you already used for the Node backend works
     here too, since this just needs a Postgres URL)
   - `CORS_ALLOWED_ORIGINS` — your deployed frontend URL (e.g. the Vercel
     domain), and set `CORS_ALLOW_ALL_ORIGINS=False` once that's set
4. Point the React frontend's API base URL at this new backend's URL instead
   of the Node one (only the base URL changes — swap `/api/signup`,
   `/api/login`, etc. calls in the frontend's axios/fetch config).

## How it fits together (for understanding, not just running it)

- **Auth**: `signup`/`login` use Django's built-in `User` model +
  `rest_framework.authtoken`. On success you get a token string; the
  frontend stores it (e.g. in memory/localStorage) and sends it back as
  `Authorization: Token <token>` on every request that needs to know who
  the user is (checkout, orders).
- **Products**: a plain `Product` model, seeded once via
  `seed_products`. Frontend just calls `GET /api/products/` and renders them.
- **Cart**: kept frontend-only (in React state), same as your Node version.
  It's only sent to the backend at checkout time as a list of
  `{product_id, quantity}`.
- **Checkout**: `CheckoutView` looks up the real prices from the DB (never
  trusts prices sent by the frontend), computes the total, creates one
  `Order` row plus one `OrderItem` row per cart line, and returns a
  confirmation message + the saved order — matching the "order placed in
  database + confirmation message" requirement.
