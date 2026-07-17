# Hostel Meal Management Sidebar and New Features Documentation

This document describes the design, implementation, and features added to Plate & Spoon to introduce the Left Sidebar (ChatGPT-style) and the associated views and APIs.

---

## 🎨 ChatGPT-Style Left Sidebar
- **Desktop Sidebar**:
  - Placed permanently on the left side of all logged-in views with a fixed layout (`lg:w-64`).
  - Utilizes a sleek, dark styling theme (`bg-slate-900 text-slate-100 dark:bg-slate-950`) to separate app actions clearly from contents.
  - Houses six primary links, administrative controls, user profiling details, and signout handles.
- **Mobile Sidebar Drawer**:
  - Hidden by default. An overlay drawer slides smoothly from the left (`-translate-x-full` to `translate-x-0`) when clicking the top bar hamburger trigger.
  - Click on the backdrop cancels/closes the sidebar drawer, resolving layout responsiveness down to `320px`.
- **Top Minimal Header**:
  - Displays the active title (based on route endpoint) and the dark/light switcher button.

---

## 🚀 Navigation Pages & Specifications

### 1. Dashboard (📊 `/dashboard`)
- Preserved the month-wide scrollable grid displaying user statistics, total costs, live meal rates, and balances. Styled outer containers to sit neatly adjacent to the new Left Sidebar.

### 2. Meal Status (🍽️ `/meal-status`)
- **Member Action**: Members toggle their daily meal choices (check/uncheck) for a rolling 7-day schedule (Today + next 6 days).
- **Meal Weights**: Checking breakfast sets `0.5`, checking lunch sets `1.0`, and checking dinner sets `1.0`. Totaling checkboxes gives the user's daily meal count.
- **Chef Lock-Out (Manager Feature)**:
  - When the chef arrives for a meal, the manager locks editing for that slot (e.g. today's breakfast) via inline lock/unlock button toggles.
  - Clicking this triggers `/api/toggle-meal-lock` to store lock records in the database.
  - Once locked, **both the manager and members** are disabled from checking/unchecking that checkbox, preventing unauthorized changes.

### 3. Today's Meals (📋 `/todays-meals`)
- Displays attendance summaries at the top showing the count of breakfast, lunch, and dinner diners for today, followed by today's overall meal tally.
- Shows a list of all active residents with ON/OFF badges next to each meal time, facilitating quick chef checkouts.

### 4. Today's Menu (🍲 `/menu`)
- Displays weekly breakfast, lunch, and dinner menus set by the manager.
- **Manager Form**: Managers can type/save meal items for each day directly into fields. Save actions update entries via AJAX to `/api/update-menu`.
- **Member View**: Displays menus in simple read-only clean text badges.

### 5. Transactions (💳 `/transactions`)
- **Hostel Purchase & Expense History**: Public ledger showing date, associated buyer, item description, and amount. Recalculates meal rate and logs audits in real-time. Managers have a "Delete" button.
- **Member Deposits & Withdrawals**: Tracks member fund movements.
- **Manager Quick Action Modals**: Managers can open overlay modals to record transactions or purchase receipts.

### 6. Member List (👥 `/members`)
- Directory showing full names, emails, roles, and status.
- **Unique ID**: Auto-provides an official formatted resident ID `MEM-XXXX` (derived from their auto-incrementing SQLite ID).

---

## 🛠️ Database Schema Changes
1. **`meals` table updates**:
   - Added `breakfast` (BOOLEAN DEFAULT 0)
   - Added `lunch` (BOOLEAN DEFAULT 0)
   - Added `dinner` (BOOLEAN DEFAULT 0)
   - Updated `meal_count` to automatically update on flag changes: `(0.5 if breakfast else 0) + (1.0 if lunch else 0) + (1.0 if dinner else 0)`.
2. **`meal_locks` table (New)**:
   - Tracks meal locks per date: `id`, `date` (Date, unique), `breakfast_locked` (Boolean), `lunch_locked` (Boolean), `dinner_locked` (Boolean).
3. **`daily_menus` table (New)**:
   - Tracks menus per date: `id`, `date` (Date, unique), `breakfast_menu` (String), `lunch_menu` (String), `dinner_menu` (String).

---

## 🔌 API Endpoints Reference
- `POST /api/toggle-meal-status`: Check/uncheck a meal slot (verifies lock checks).
- `POST /api/toggle-meal-lock`: Freeze/unfreeze editing for a specific meal and date (manager only).
- `POST /api/update-menu`: Update daily breakfast/lunch/dinner menus (manager only).
- `GET /api/get-all-transactions`: Fetches deposits/withdrawals (re-routed to `@login_required` for transparency).
