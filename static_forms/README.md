# static_forms

Положите сюда JSON-файл(ы) со спарсенными анкетами, например `forms.json`.

## Формат `forms.json`
```json
[
  {
    "name": "Алина",
    "age": 22,
    "height": 170,
    "weight": 52,
    "bust_size": 3,
    "photos": [
      "https://example.com/1.jpg",
      "https://example.com/2.jpg"
    ]
  }
]
```

Запуск импорта в БД:
```bash
docker compose run --rm -v "$(pwd)":/workspace -w /workspace api python import_static_forms.py
```
