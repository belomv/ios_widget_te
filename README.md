# iOS-виджет для Training Endurance

Виджет для iOS показывает тренировки из календаря [Training Endurance](https://trainingendurance.com/en/)
(веб-приложение: `app.trainingendurance.com`). Аккаунт бесплатный, публичного API нет.

## Где мы сейчас

- **Этап 1 (источник данных) — готов.** Данные берём из того же GraphQL API, что использует веб-приложение TE,
  вход по email и паролю, сессия живёт ~3 года. Проверено на бесплатном аккаунте.
  Коротко — [DECISION.md](docs/01-data-source/DECISION.md), подробно — [эксперимент A](docs/01-data-source/experiments/A-private-web-api.md).
- **Дальше — этап 2:** какие поля нужны виджету и как приложение их получает ([PLAN.md](docs/PLAN.md)).
  Ждём ответов на [вопросы](docs/QUESTIONS.md) 1, 5 и 7.

## Где что лежит

| Файл | Зачем |
|---|---|
| [`docs/PLAN.md`](docs/PLAN.md) | Этапы проекта и критерии готовности каждого |
| [`docs/PROGRESS.md`](docs/PROGRESS.md) | Журнал: что сделано, когда, что узнали |
| [`docs/QUESTIONS.md`](docs/QUESTIONS.md) | Открытые вопросы к владельцу проекта |
| [`docs/01-data-source/options.md`](docs/01-data-source/options.md) | Все варианты получения данных, оценка каждого |
| [`docs/01-data-source/experiments/`](docs/01-data-source/experiments/) | По файлу на каждую проверку варианта (шаблон: `_template.md`) |
| [`docs/01-data-source/DECISION.md`](docs/01-data-source/DECISION.md) | Итог этапа: какой способ выбрали и почему |
| [`docs/02-widget/examples/`](docs/02-widget/examples/README.md) | Реальные примеры тренировок для дизайна виджета |
| [`tools/te-probe/`](tools/te-probe/) | Прототип: вход в TE и тренировки на неделю ([как запустить](tools/te-probe/README.md)) |

Следующие этапы (виджет, приложение) получат свои папки `docs/02-…`, `docs/03-…` по той же схеме:
`options` → `experiments` → `DECISION`.

## Правило про секреты

Логины, пароли, токены, cookies и HAR-дампы в репозиторий не коммитим. Для них есть `secrets/` и `*.har`
в `.gitignore`. В облачном окружении логин и пароль TE заданы переменными `TE_EMAIL` и `TE_PASSWORD`
(настройки окружения), а не файлами. В отчётах об экспериментах оставляем только структуру запросов и ответов, без значений.
