# Примеры реальных данных для дизайна виджета

Выгрузки из календаря TE. На них проверяем макеты: длина заголовков и комментариев, статусы, заметки.

| Файл | Что внутри |
|---|---|
| [`week-2026-09-21.md`](week-2026-09-21.md) / [`.json`](week-2026-09-21.json) | Неделя 21–27.09.2026: заголовки, комментарии тренера, выполнено или нет |

Поля в JSON: `date`, `weekday`, `kind` (`workout` / `event`), `title`, `sport`, `coach_comment`,
`athlete_comment`, `uploaded` (есть загруженная тренировка), `uploaded_from` (откуда), `status`
(`done` / `missed` / `today` / `planned`), `created_by` (`coach` / `athlete`).

Макеты — в Penpot, описание дизайна — [`../DESIGN.md`](../DESIGN.md).
