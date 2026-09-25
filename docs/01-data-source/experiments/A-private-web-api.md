# Эксперимент A: приватный API веб-приложения

- **Вариант:** [options.md → A](../options.md#a-приватный-api-веб-приложения)
- **Статус:** ✅ работает на бесплатном аккаунте. Прототип входит по логину и паролю и отдаёт тренировки на неделю.
- **Дата:** 2026-09-25

## Гипотеза
Календарь в `app.trainingendurance.com` загружается JSON-запросами с токеном, которые можно повторить
из кода. Токен живёт достаточно долго или обновляется без участия пользователя.

## Что сделал
1. Скачал `index.html` и все JS-чанки SPA (~110 файлов, 7 МБ; Vite/rolldown, React + Apollo Client,
   сборка `09.22.7d`). Source maps не выложены (404).
2. Нашёл конфиг (`config-*.js`) с адресами сервисов, достал из бандла все 203 GraphQL-операции
   (они лежат строками в `gql`-шаблонах в `hooks-*.js`).
3. Проверил `/graphql` и Kratos без авторизации; скачал схему через интроспекцию.
4. Написал прототип [`tools/te-probe/te_probe.py`](../../../tools/te-probe/te_probe.py) и проверил, что
   его запросы проходят валидацию схемы.
5. Прогнал прототип на реальном (бесплатном) аккаунте — см. «Прогон на реальном аккаунте» ниже.

## Результат

### Сервисы (из `config-*.js`)
| Что | URL |
|---|---|
| GraphQL API | `https://app.trainingendurance.com/graphql` |
| Ory Kratos (аутентификация) | `https://app.trainingendurance.com/kratos` |
| Страница входа (UI) | `https://auth.trainingendurance.com` |
| Realtime (websocket) | `https://app.trainingendurance.com/realtime` |
| OAuth 2.1 (Ory Hydra) | `https://oauth.trainingendurance.com` (см. «Официальный OAuth / MCP» ниже) |
| MCP-сервер | `https://mcp.trainingendurance.com` |

Для доменов `.ru` те же адреса с `trainingendurance.ru`.

### Авторизация
- Аутентификация на **Ory Kratos**. Способы входа (из `GET /kratos/self-service/login/api`):
  `password` (email + пароль), `code` (одноразовый код на почту), `oidc` через **Google** и **Apple**.
- Kratos отдаёт **нативный (API) поток** входа `GET /kratos/self-service/login/api` →
  `POST <ui.action>` с `{"method":"password","identifier":…,"password":…}`. Cookies и CSRF не нужны,
  в ответ приходит `session_token`. Это штатный способ Kratos для мобильных приложений.
  Проверено: на неверные данные сервер отвечает 400 с понятным сообщением.
- GraphQL принимает сырой `session_token` в заголовке **`x-session-token`** (проверено на аккаунте).
  `Authorization: Bearer` ждёт не сам токен, а JWT из `GET /kratos/sessions/whoami?tokenize_as=long_lived_token`
  (так делает веб-приложение; JWT живёт **30 дней**). Для нас проще `x-session-token`.
- Проверка сессии: `GET /kratos/sessions/whoami` с заголовком `X-Session-Token` (без токена 401).
- **Срок жизни сессии: ~1000 дней** (вход 2026-09-25 → `expires_at` 2029-06-21). Refresh не нужен:
  приложение входит один раз, хранит токен в Keychain, а при 401/`ErrAccessDenied` входит заново.
- Если аккаунт создан через Google/Apple и пароля нет, запасной путь — метод `code` (код на почту)
  или один вход через WebView (вариант F), после которого забираем `kratos_session_token`.

### GraphQL
- **Интроспекция открыта без авторизации**: 513 типов, 103 query. Данные без токена не отдаются:
  `calendarItems` → `ErrAccessDenied`.
- Календарь:
  - `calendarItems(p: CalendarItemsRequest!)`, где `CalendarItemsRequest { userID, ids, dates: [Date!], tagIds }`.
    Даты передаются списком (`["2026-09-25", …]`), не диапазоном.
  - `calendarItemsBatch(requests: [...])` — пакетный вариант, им пользуется веб-приложение.
  - `calendarOverview(p: {userID, startDate, endDate})` → по дням количество `workouts/events/menus/rests`.
- `CalendarItem { id, userID, date, sort, type: WORKOUT|EVENT|REST|MENU, data: Activity, tags, visibility }`,
  `Activity` — union `Workout | Rest | Event | Menu`.
- Поля тренировки, полезные виджету (`Workout`):
  `name`, `workoutType` (`RUNNING, BIKE, SWIM, SKI, WALK, OTHER, STRENGTH`), `description`,
  `manualDone`, `plan` / `fact` (`WorkoutMetric`: `duration` в секундах, `distance` в метрах, `ess`,
  `etvs`, пульс, калории, время в зонах), `struct` (шаги с зонами), `feeling`, `exertion`, комментарии.
- Кто я: `query getMe { userInfo { id email role … } }`. `userID` нужен в запросе календаря.

### Официальный OAuth / MCP (побочная находка)
- `mcp.trainingendurance.com` — официальный MCP-сервер (162 инструмента), авторизация OAuth 2.1
  (PKCE + Dynamic Client Registration) через `oauth.trainingendurance.com`. Скоупы: `training:read`,
  `offline_access` и др. Есть `device_code` grant.
- На странице сервера прямо сказано: **доступен только PRO-атлетам и платным тренерам**, остальным
  после входа вернётся 403. Для бесплатного аккаунта не подходит. Принимает ли `/graphql`
  OAuth-токены Hydra, не проверено.

### Признаки варианта B
- В схеме и бандле нет iCal / `.ics` / webcal / публичных ссылок на календарь.
- Зато в настройках интеграций есть провайдер **Google Calendar** (`Provider.GOOGLECALENDAR`), текст:
  «При включении все запланированные тренировки будут автоматически выгружаться в ваш Google Calendar».
  Подробности в [B-builtin-export.md](B-builtin-export.md).

## Прототип
[`tools/te-probe/te_probe.py`](../../../tools/te-probe/te_probe.py) (Python 3, только стандартная библиотека):
1. Берёт `TE_EMAIL` и `TE_PASSWORD` из переменных окружения или `secrets/te.env` (или готовый `TE_SESSION_TOKEN`).
2. Входит через нативный поток Kratos, сохраняет токен и `expires_at` в `secrets/te-session.json` (0600).
   При следующем запуске проверяет токен через `whoami` и заново входит только если он истёк.
3. `getMe` → `calendarItems` на N дней → печатает: дата, отметка «выполнено», вид спорта, название,
   план и факт (длительность, дистанция). С `--json` печатает сырой ответ.

Проверено без аккаунта: оба запроса проходят валидацию схемы (на них приходит `ErrAccessDenied`,
а не 422), поток входа отрабатывает до ответа «неверные учётные данные».

## Прогон на реальном аккаунте (2026-09-25)
- Вход по паролю через нативный поток Kratos — ✅. Аккаунт `ATHLETE`, PRO нет (`permissions.proUntil = null`).
- `getMe` и `calendarItems` — ✅, данные отдаются бесплатному аккаунту.
- Вывод прототипа на 7 дней (2 будущие тренировки: `RUNNING` «Лыжная имитация», `BIKE` «Вело длинная»).
- Что видно за 2 недели: у выполненных тренировок заполнен `fact` (длительность, дистанция, ESS); у запланированных
  `plan` заполнен, только если его указали при создании (в одной — 76 мин плана плюс структура из шагов, в других
  только название). Бывают записи `EVENT` (заметки на день) рядом с тренировками.
- `syncWithProviders` у тренировки показывает, куда она выгружена (Coros, Garmin) — пригодится для диагностики.
- Капчи и ограничения частоты при нескольких запросах не встретил.

## Что осталось
- [x] Прогнать прототип на реальном аккаунте.
- [x] Срок жизни сессии: ~1000 дней.
- [x] Бесплатному аккаунту отдаются `plan`/`fact`.
- [ ] Для виджета: если `plan.duration` пуст, считать длительность по `struct` (сумма шагов × repeat).

## Вывод
**Берём A как основной способ.** Официальный механизм Kratos для нативных клиентов, один GraphQL-запрос
на неделю, все нужные поля есть, сессия живёт почти 3 года. Риск: API недокументированный и может
поменяться, поэтому разбор ответа надо делать терпимым к новым и пропавшим полям.
