# Data model

SQLite tables:
- `transactions`: id, description, positive amount, category, date and created timestamp.
- `goals`: id, title, target amount, saved amount and optional target date.
- `invoices`: id, customer label, taxable amount, GST rate, total, status and timestamp.

The prototype has no user table, authentication or tenant boundary. All local records are shared by whoever can access the running instance. Do not store real financial records in a public demo.
