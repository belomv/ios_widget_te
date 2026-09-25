# Эксперимент A: приватный API веб-приложения

- **Вариант:** [options.md → A](../options.md#a-приватный-api-веб-приложения)
- **Статус:** 🟡 в работе. Разбор без входа в аккаунт закончен, API найден и понятен. Прототип написан
  и проверен на схеме. Осталось прогнать его на реальном аккаунте (нужны логин и пароль).
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
- GraphQL принимает токен в заголовке **`Authorization: Bearer <kratos_session_token>`** (так делает
  Apollo-клиент веб-приложения). Браузер вдобавок шлёт cookie; есть и устаревшие заголовки
  `x-session-token`, `x-session-cookie-support`.
- Проверка сессии: `GET /kratos/sessions/whoami` с заголовком `X-Session-Token` (без токена 401).
- **Срок жизни сессии пока неизвестен**, узнаем после первого входа (поле `expires_at`). Refresh-токена
  у сессий Kratos нет, поэтому когда сессия истечёт, придётся войти заново тем же логином и паролем.
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
1. Берёт `TE_EMAIL` и `TE_PASSWORD` из `secrets/te.env` (или готовый `TE_SESSION_TOKEN`).
2. Входит через нативный поток Kratos, сохраняет токен и `expires_at` в `secrets/te-session.json` (0600).
   При следующем запуске проверяет токен через `whoami` и заново входит только если он истёк.
3. `getMe` → `calendarItems` на N дней → печатает: дата, отметка «выполнено», вид спорта, название,
   план и факт (длительность, дистанция). С `--json` печатает сырой ответ.

Проверено без аккаунта: оба запроса проходят валидацию схемы (на них приходит `ErrAccessDenied`,
а не 422), поток входа отрабатывает до ответа «неверные учётные данные».

## Что осталось
- [ ] Запустить прототип на реальном аккаунте: `secrets/te.env` → `python3 tools/te-probe/te_probe.py`.
- [ ] Записать срок жизни сессии (`expires_at`) и проверить, продлевается ли он.
- [ ] Проверить, что бесплатному аккаунту отдаются `plan`/`fact` (ограничения тарифа на сервере).
- [ ] Проверить, не мешают ли входу капча или ограничение частоты запросов.

## Вывод (предварительный)
Вариант A реален и технически очень удобен для iOS: официальный механизм Kratos для нативных клиентов,
один GraphQL-запрос на неделю, все нужные поля есть. Главный открытый вопрос — срок жизни сессии.
Если он короткий, приложению придётся хранить пароль в Keychain и входить заново само.
