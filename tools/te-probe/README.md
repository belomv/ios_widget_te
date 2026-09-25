# te-probe

Прототип источника данных (этап 1, вариант A): входит в Training Endurance по email и паролю и печатает
тренировки из календаря. Python 3, без сторонних библиотек.

## Запуск

Логин и пароль берутся из переменных окружения `TE_EMAIL` и `TE_PASSWORD` (в облачном окружении они уже
заданы) или из файла `secrets/te.env`:

```
TE_EMAIL=you@example.com
TE_PASSWORD=...
```

```bash
python3 tools/te-probe/te_probe.py                 # 7 дней начиная с сегодня
python3 tools/te-probe/te_probe.py --days 14       # две недели
python3 tools/te-probe/te_probe.py --start 2026-09-20 --json   # сырой ответ API
python3 tools/te-probe/te_probe.py --login         # войти заново, не используя сохранённый токен
```

После первого входа токен сохраняется в `secrets/te-session.json` и используется повторно, пока жив (~1000 дней).

## Пример вывода (2026-09-20 … 27)

```
2026-09-20   EVENT    Пробежка 10-15км
2026-09-20 ✓ RUNNING  Morning Run                              план                   факт  51 мин   9.5 км
2026-09-22   EVENT    Без первозмоганий
2026-09-22 ✓ RUNNING  Кросс + спринты                          план    1:16           факт    1:23  14.4 км
2026-09-24 ✓ BIKE     Пороговая мягкая                         план                   факт    1:38  50.2 км
2026-09-26   RUNNING  ЛЫжна имитация                           план                   факт
2026-09-27   BIKE     Вело длинная                             план                   факт
```

`✓` — тренировка выполнена, `EVENT` — заметка на день. Пустой план значит, что в TE у тренировки задано только название.

## Как устроено

1. `GET /kratos/self-service/login/api` → `POST` на адрес из ответа с email и паролем → `session_token`.
2. `POST /graphql` с заголовком `x-session-token`: `getMe` (id пользователя), затем `calendarItems` со списком дат.

Подробности — в [эксперименте A](../../docs/01-data-source/experiments/A-private-web-api.md).
