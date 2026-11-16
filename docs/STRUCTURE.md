# STRUCTURE

Ниже зафиксирован стартовый каркас `new_escort/`.

```text
new_escort/
├── api/
│   ├── api/routes/{client,admin,support,internal}/v1/
│   ├── core/
│   ├── db/
│   ├── domain/{clients,forms,logs,orders,settings,support}/
│   ├── repositories/
│   ├── models/{clients,forms,orders,settings,addresses}.py
│   ├── schemas/{client,admin,support,internal}/
│   ├── clients/{photos,logs,external}/
│   ├── migrations/versions/
│   └── tests/
├── main/
│   ├── core/
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── start.py
│   │   │   ├── info.py
│   │   │   ├── support.py
│   │   │   ├── models.py
│   │   │   ├── models_catalog.py
│   │   │   ├── models_order.py
│   │   │   ├── models_payment.py
│   │   │   ├── search_with_code.py
│   │   │   ├── profile.py
│   │   │   └── address.py
│   │   ├── keyboards/
│   │   │   ├── start.py
│   │   │   ├── info.py
│   │   │   ├── support.py
│   │   │   ├── models.py
│   │   │   ├── models_catalog.py
│   │   │   ├── models_order.py
│   │   │   ├── models_payment.py
│   │   │   ├── search_with_code.py
│   │   │   ├── profile.py
│   │   │   └── address.py
│   │   ├── assets/texts/
│   │   └── states/
│   ├── clients/{api,logs}/
│   └── tests/
├── support/
│   ├── core/
│   ├── bot/{handlers,keyboards,assets/texts,states}/
│   ├── clients/{api,logs}/
│   └── tests/
├── admin/
│   ├── core/
│   ├── bot/{handlers,keyboards,assets/texts,states}/
│   ├── clients/api/
│   └── tests/
├── web_app/
│   ├── backend/{core,api/routes,clients/api,tests}/
│   └── frontend/{public,src}/
├── photos/
│   ├── core/
│   ├── api/routes/{internal/v1,public}/
│   ├── services/{storage,media}/
│   ├── schemas/
│   └── tests/
├── logs/
│   ├── core/
│   ├── api/routes/v1/
│   ├── services/{telegram,history}/
│   ├── schemas/
│   ├── assets/texts/
│   └── tests/
├── shared/
│   ├── auth/
│   ├── db/
│   ├── http/
│   ├── bot/
│   ├── server/
│   ├── texts/
│   ├── utils/
│   └── schemas/
├── docs/
├── scripts/
├── deploy/
├── .env.example
└── docker-compose.yml
```
