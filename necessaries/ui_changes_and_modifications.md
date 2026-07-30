# Hostel Meal Management UI and Logic Modifications

This document outlines the changes, styling enhancements, features, and model upgrades introduced to the Hostel Meal Management System (Plate & Spoon).

---

## 🚀 Key Improvements & Modifications

### 1. Favicon Integration (Plate & Spoon)
- Designed a custom vector favicon: [favicon.svg](../static/favicon.svg).
- Displays a stylish indigo/blue gradient plate paired with a slate/silver spoon.
- Injected the SVG icon references into both [base.html](../templates/base.html) and [login.html](../templates/login.html).

### 2. Premium Light & Dark Mode
- Added theme settings to Tailwind's layout engine.
- Configured a floating toggle switch (with solar/lunar icons) in the top-right corner of the login screen and within the main sticky navbar.
- Implemented an inline script in `<head>` to detect the previous choice (`localStorage.getItem('theme')`) and execute an instantaneous render transition, preventing flashing/white-flickering.
- Re-styled page layouts, cards, modals, dropdown drawers, and buttons using standard `dark:` variant classes (matching deep slate and indigo hues).

### 3. Expense Section Enhancements (Paid By Association)
- **Model Modifications**:
  - Updated the `Expense` model in [models.py](../models.py) to include `user_id` linked as a foreign key to the `users` table, plus a back-reference relationship (`user`).
- **Database Schema Upgrades**:
  - Added a startup database migration inside `create_app()` within [app.py](../app.py). This block dynamically executes `ALTER TABLE expenses ADD COLUMN user_id INTEGER` if the column doesn't exist.
- **Route Access & API Overhaul**:
  - Upgraded `/api/add-expense` to receive and process `user_id` from JSON requests.
  - Re-routed `/api/get-expenses` from `@manager_required` to `@login_required` so all members can view list entries.
  - Included `user_name` (e.g. `'Spent by: Mehedi'`) in JSON payloads returned by `/api/get-expenses`.
- **UI Integrations**:
  - Integrated a "Paid By" select dropdown in the manager's addition panel inside [manager.html](../templates/manager.html).
  - Designed a transparent shared expense history widget inside [dashboard.html](../templates/dashboard.html) for regular member inspection, listing the spent-by name on the side.

### 4. Decimal Radix Formatting
- Preserved all mathematical calculations precisely as requested.
- Standardized the user interface to format the meal rate to exactly 2 digits after the decimal point using the Jinja formatting tag `{{ "%.2f"|format(meal_rate) }}`.

### 5. Smart Phone & Mobile Responsiveness
- Redesigned the primary table inside [dashboard.html](../templates/dashboard.html). Large screens render the full, multi-column meal grid, while small screens (<1024px) load interactive member cards.
- Added expandable meal-breakdown drawers per user card so mobile users can view daily meals.
- Standardized glassmorphic drawer elements, responsive grid flexports, and input alignments to display beautifully down to 320px viewport widths.
