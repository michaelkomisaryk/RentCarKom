# rentCarKom 🚗

A full-featured car rental CRM built with Python + Flet.

## Quick Start

```bash
pip install 'flet>=0.80'
python main.py
# Opens at http://localhost:8080
```

---

## Авторизація (сесія)

Усі сторінки, крім логіну, доступні **лише після входу**. Якщо відкрити `/home` або `/car/...` без логіну, вас перенаправить на `/`.

| Role    | Email                       | Password      |
|---------|-----------------------------|---------------|
| Admin   | admin@rentcarkom.com        | `Admin123!`   |
| Manager | manager@rentcarkom.com      | `Manager123!` |

> Нові користувачі через реєстрацію отримують роль **client**. Пароль має бути **надійним** (див. нижче).

> Якщо у вас уже є старий `data/db.json` з паролями `admin123` / `manager123`, або видаліть файл для «чистого» сиду, або оновіть паролі в JSON вручну.

### Вимоги до пароля при реєстрації

- щонайменше **8** символів, без пробілів;
- латиниця: **велика** (A–Z) і **мала** (a–z) літера;
- хоча б одна **цифра**;
- хоча б один **спецсимвол** (`!@#$%…`);
- перевірка **email** та **імені** (літери UA/EN, пробіл, `-` `'` `.`).

> Режим гостя без пароля **вимкнено** — потрібен обліковий запис.

---

## Role Permissions

| Feature                  | Client | Manager | Admin |
|--------------------------|--------|---------|-------|
| Browse cars              | ✅     | ✅      | ✅    |
| View car details         | ✅     | ✅      | ✅    |
| Rent a car               | ✅     | ✅      | ✅    |
| View stats dashboard     | ❌     | ✅      | ✅    |
| View all rentals         | ❌     | ✅      | ✅    |
| Complete/Cancel rentals  | ❌     | ✅      | ✅    |
| Add new cars             | ❌     | ❌      | ✅    |
| Add photos to cars       | ❌     | ❌      | ✅    |
| Delete cars              | ❌     | ❌      | ✅    |

---

## Data Storage

All data is saved in `data/db.json`. File is created automatically on first run.

### Rental fields stored:
- `id`, `car_id`, `car_brand`, `car_model`, `car_plate`
- `user_id`, `user_email`, `renter_name`
- `start_datetime`, `end_datetime`, `days`
- `price_per_day`, `total_price`
- `status` (active / completed / cancelled)
- `created_at`

---

## Project Structure

```
rentCarKom/
├── main.py                    # Entry point + routing
├── data/
│   └── db.json                # Auto-generated JSON database
├── assets/
│   ├── cars/                  # Car photos organized by car ID
│   └── uploads/               # Temp folder for web uploads
└── src/
    ├── database.py            # All DB read/write logic
    ├── state.py               # Session state (current user)
    ├── auth_validation.py     # Email / name / password rules (registration)
    ├── neon_ui.py             # Neon icon frames + hover glow
    ├── ui_helpers.py          # SnackBar, image paths, errors
    ├── components/
    │   ├── header.py          # Top app bar with role badge
    │   └── car_card.py        # Car list card with status
    └── views/
        ├── login_view.py      # Login + Registration screen
        ├── home_view.py       # Car listing with filters + stats
        ├── car_detail_view.py # Car detail + gallery + rental form
        ├── add_car_view.py    # Admin: add car with photos
        └── rentals_view.py    # Admin/Manager: rentals table
```
