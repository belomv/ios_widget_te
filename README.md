# iOS-виджет для Training Endurance

Виджет для iOS показывает тренировки из календаря [Training Endurance](https://trainingendurance.com/en/)
(веб-приложение: `app.trainingendurance.com`). Аккаунт бесплатный, публичного API нет, так что первая
задача — найти способ получать данные.

## Где что лежит

| Файл | Зачем |
|---|---|
| [`docs/PLAN.md`](docs/PLAN.md) | Этапы проекта и критерии готовности каждого |
| [`docs/PROGRESS.md`](docs/PROGRESS.md) | Журнал: что сделано, когда, что узнали |
| [`docs/QUESTIONS.md`](docs/QUESTIONS.md) | Открытые вопросы к владельцу проекта |
| [`docs/01-data-source/options.md`](docs/01-data-source/options.md) | Все варианты получения данных, оценка каждого |
| [`docs/01-data-source/experiments/`](docs/01-data-source/experiments/) | По файлу на каждую проверку варианта (шаблон: `_template.md`) |
| [`docs/01-data-source/DECISION.md`](docs/01-data-source/DECISION.md) | Итог этапа: какой способ выбрали и почему |

Следующие этапы (виджет, приложение) получат свои папки `docs/02-…`, `docs/03-…` по той же схеме:
`options` → `experiments` → `DECISION`.

## Правило про секреты

Логины, пароли, токены, cookies и HAR-дампы в репозиторий не коммитим. Для них есть `secrets/` и `*.har`
в `.gitignore`. В отчётах об экспериментах оставляем только структуру запросов и ответов, без значений.
