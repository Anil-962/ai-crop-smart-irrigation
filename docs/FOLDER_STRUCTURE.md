# Folder Structure - AGROGUARD AI

```text
ai-crop-smart-irrigation/
  app/
    routes/
      health.py
      predict.py
      decision.py
    services/
      factory.py
      disease_service.py
      irrigation_service.py
      weather_service.py
      decision_service.py
    utils/
      errors.py
      images.py
      validation.py
    __init__.py
    config.py
  docs/
    API_CONTRACT.md
    FOLDER_STRUCTURE.md
  train/
    data/
      .gitkeep
    requirements-train.txt
    train_disease.py
    train_irrigation.py
    README.md
  models/
    .gitkeep
  Dockerfile
  docker-compose.yml
  .dockerignore
  .env.example
  requirements.txt
  run.py
  README.md
```

## Notes

- `routes/` handles Flask endpoint definitions only.
- `services/` contains model loading, inference, and recommendation logic.
- `utils/` contains validation and input parsing helpers.
- `models/` is where trained artifacts should be placed:
  - `models/disease_model.h5` for CNN
  - `models/irrigation_model.pkl` for irrigation regressor
