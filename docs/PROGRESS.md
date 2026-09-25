# Журнал

Новые записи сверху. Формат: дата — что сделали → что узнали → что дальше.

## 2026-09-25 — Старт, разведка

- Сделал структуру документов (`README`, `PLAN`, `PROGRESS`, `QUESTIONS`, `docs/01-data-source/`).
- Нашёл сервис: Training Endurance (trainingendurance.com, разработчик Artem Smirnov). Есть веб-приложение
  `app.trainingendurance.com`, приложения для iOS и Android. Заявлены интеграции: импорт выполненных
  тренировок из Garmin/Polar/Wahoo/Suunto/Strava, экспорт тренировок в Garmin/Polar/Wahoo/Suunto/Apple Watch.
- Публичного API, iCal-экспорта или документации для разработчиков поиск не нашёл. Это не значит, что их нет:
  нужно проверить руками в настройках.
- Собрал 9 вариантов получения данных → [options.md](01-data-source/options.md).
- **Блокер:** из облачного окружения, где я работаю, закрыт сетевой доступ к `trainingendurance.com`,
  `app.trainingendurance.com`, `apps.apple.com`, `play.google.com`. Сам открыть веб-приложение и посмотреть
  его запросы я пока не могу. Варианты: открыть эти домены в настройках окружения или снять запросы
  в браузере самому (инструкция в [эксперименте A](01-data-source/experiments/A-private-web-api.md)).

**Дальше:** ответы на [вопросы](QUESTIONS.md) → проверки B, A, G.
