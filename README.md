# sync-player

Telegram Mini App для совместного просмотра видео: комнаты, общий плеер, который держит всех
на одном таймкоде, и чат в реальном времени. Владелец комнаты управляет воспроизведением,
остальные смотрят синхронно.

```
Telegram WebApp  →  FastAPI (REST + WebSocket)  →  Redis (player state)
                            ↓                              ↓
                      React 19 + Vite            yt-dlp + ffmpeg (прокси потока)
```

---

## 🇬🇧 English

Watch-party Telegram Mini App. The room owner controls playback (play/pause/seek) and
loads a video by URL or YouTube search; every participant's player follows the shared
state. Rooms are private or invite-only, and each one has a real-time chat.

**Stack:** FastAPI, SQLAlchemy 2 (async), SQLite + Redis, WebSockets, yt-dlp/ffmpeg,
React 19, Vite, nginx.

---

## Возможности

- **Комнаты** — создание, пароль, приватность, список в лобби.
- **Синхронизация** — владелец играет/ставит на паузу/перематывает, остальные повторяют.
  Расхождение больше 2 секунд автоматически выравнивается.
- **Загрузка видео** — поиск по YouTube (`ytsearch10`) или вставка прямой ссылки.
  Поток проксируется через backend: `yt-dlp` достаёт прямые URL видео и аудио,
  `/api/player/stream` проксирует их с поддержкой `Range` и переписывает `.m3u8`-плейлисты.
- **Раздельные аудио и видео** — если источник отдаёт их разными потоками, аудио
  становится мастер-клоком, а видео подгоняется под него (допуск 0.3 с).
- **Чат** — сообщения через WebSocket, хранятся в БД, поддерживается удаление своих.
- **Участники** — роли `owner` / `guest`, вход по инвайт-коду.
- **Проверка рассинхрона** — сервер умеет считать дельту между таймкодом клиента и
  состоянием комнаты (WS-действие `check_desync`).
- **Полноэкранный режим**, тактильный отклик и кнопка «назад» через Telegram API.
- **HLS** — воспроизведение `.m3u8` через `hls.js`.

## Стек

| Слой | Технологии |
| --- | --- |
| Backend | Python 3.12 / 3.13, FastAPI, uvicorn |
| ORM / БД | SQLAlchemy 2 (async), aiosqlite (SQLite) |
| Состояние плеера | Redis (`redis.asyncio`) |
| Real-time | WebSockets (`websockets`, uvicorn) |
| Видео | yt-dlp, ffmpeg, httpx (прокси потока) |
| Auth | HMAC-SHA256 валидация `initData` из Telegram |
| Frontend | React 19, Vite, React Router 7, motion, hls.js |
| Reverse proxy | nginx |
| Тесты | pytest, pytest-asyncio, httpx |

## Быстрый старт

### 1. Docker (весь стек одной командой)

```bash
git clone https://github.com/Yarfer800/sync-player.git
cd sync-player
cp .env.example .env      # подставьте свой токен бота
docker compose up --build
```

- Фронтенд — http://localhost
- API — http://localhost:8000 (Swagger: http://localhost:8000/docs)
- Redis — localhost:6379

### 2. Локально, без Docker

**Backend:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # или: uv sync
cp .env.example .env                # заполнить token / database_url / admin_id
python main.py                      # uvicorn с reload на :8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev                         # http://localhost:5173
```

Vite проксирует `/api` и `/api/ws` на `http://localhost:8000`, так что CORS в dev не мешает.

## Конфигурация

Переменные читаются из `.env` в корне (`app/core/config.py`).

| Переменная | Обязательна | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `TOKEN` | да | — | токен Telegram-бота; ключ для проверки подписи `initData` |
| `DATABASE_URL` | да | — | SQLAlchemy async URL, например `sqlite+aiosqlite:///app.db` |
| `ADMIN_ID` | да | — | Telegram ID администратора |
| `REDIS_URL` | нет | `redis://localhost:6379` | Redis для состояния плеера |

Переменные фронтенда (`.env` в `frontend/`):

| Переменная | Назначение |
| --- | --- |
| `VITE_API_URL` | база API, по умолчанию `/api` (nginx/Vite-прокси) |
| `VITE_MOCK_INIT_DATA` | поддельный `initData` для локальной разработки без Telegram |

> При добавлении своего домена в `app/app.py` не забудьте внести его в `allow_origins`
> у `CORSMiddleware` — там захардкожен список (`localhost:5173`, `localhost:8000`,
> Vercel-домен).

## Структура проекта

```
app/
  api/
    deps.py            зависимости FastAPI, валидация initData, провайдеры репозиториев
    routes/            users, rooms, messages, player, search, ws
  core/config.py       pydantic-settings
  db/                  engine, модели (users, rooms, room_participants, messages), redis
  repositories/        доступ к данным, один класс на сущность
  schemas/             pydantic-схемы запросов/ответов
  services/            player (yt-dlp), player_state, websocket, web_search
frontend/src/
  api/                 HTTP-клиент и WebSocket-обёртка
  components/          layout, lobby, room, ui
  context/             AuthContext
  hooks/               useRoom, useMessages, usePlayerState, useWebSocket
  pages/               LobbyPage, RoomPage, ProfilePage
  utils/telegram.js    initData, haptic, back button
tests/                 pytest: API, репозитории, плеер, поиск
```

Слои идут строго сверху вниз: `routes → services → repositories → db`.
Репозитории не знают про HTTP, бизнес-логика живёт в `services` и роутах.

## Аутентификация

Никаких паролей и JWT — только Telegram.

1. Фронтенд читает `window.Telegram.WebApp.initData` (в dev — `VITE_MOCK_INIT_DATA`).
2. Отправляет его в заголовке `X-Init-Data` (для WebSocket — в query-параметре `init_data`).
3. `validate_init_data()` пересобирает data-check-строку, считает
   `HMAC-SHA256(HMAC-SHA256("WebAppData", token), data_check_string)`
   и сверяет с `hash` через `hmac.compare_digest`.
4. Пользователь создаётся в БД при первом запросе, `username` синхронизируется на каждом входе.

## API

Все маршруты под префиксом `/api`. Фронтенд шлёт `X-Init-Data` с каждым запросом;
на мутациях (`POST` / `PUT` / `PATCH` / `DELETE`) подпись проверяется обязательно, а
`GET`-ручки комнат, участников и сообщений сейчас открыты.

### Users

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/users/me` | текущий пользователь |
| `PATCH` | `/api/users/me` | обновить `username` |

### Rooms

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/rooms` | список комнат с количеством участников |
| `POST` | `/api/rooms` | создать комнату (создатель становится `owner`) |
| `GET` | `/api/rooms/{room_id}` | комната со списком участников |
| `DELETE` | `/api/rooms/{room_id}` | удалить комнату (только `owner`) |
| `POST` | `/api/rooms/{room_id}/join` | войти по паролю |
| `POST` | `/api/rooms/{room_id}/leave` | выйти |
| `POST` | `/api/rooms/{room_id}/invite` | выпустить инвайт-код (только `owner`) |
| `POST` | `/api/rooms/join/invite` | войти по инвайт-коду |
| `GET` | `/api/rooms/{room_id}/participants` | участники комнаты |

### Player state

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/rooms/{room_id}/player/state` | текущее состояние плеера |
| `POST` | `/api/rooms/{room_id}/player/state` | создать состояние (только `owner`) |
| `PUT` | `/api/rooms/{room_id}/player/state` | обновить состояние + рассылка участникам (только `owner`) |

```json
{
  "room_id": 1,
  "current_timecode": 42.5,
  "video_source_link": "https://www.youtube.com/watch?v=...",
  "is_paused": true
}
```

### Player (видео)

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/api/player/info` | метаданные + прямые URL видео/аудио (`yt-dlp`) |
| `POST` | `/api/player/download` | скачать фрагмент по таймкодам, отдаётся файлом |
| `GET` | `/api/player/stream?url=...` | прокси потока с `Range` и переписыванием HLS-плейлиста |

### Messages и поиск

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/rooms/{room_id}/messages` | история сообщений (`limit` 1–500, `offset`) |
| `POST` | `/api/rooms/{room_id}/messages` | отправить сообщение (+ рассылка) |
| `DELETE` | `/api/rooms/{room_id}/messages/{message_id}` | удалить своё сообщение |
| `GET` | `/api/search?query=...` | поиск видео на YouTube |

## WebSocket

Подключение: `ws(s)://<host>/api/ws/rooms/{room_id}?init_data=<initData>`

Клиент шлёт `{"action": "...", "payload": {...}}`:

| Действие | Payload | Ответ сервера |
| --- | --- | --- |
| `send_message` | `{text, image?}` | рассылка `new_message` всей комнате |
| `check_desync` | `{timecode}` | лично клиенту `desync_result` с `desync_seconds` и `room_timecode` |

Сервер шлёт:

| Событие | Когда |
| --- | --- |
| `new_message` | новое сообщение в комнате (WS или REST) |
| `player_state_updated` | владелец обновил состояние плеера |
| `desync_result` | ответ на `check_desync` |

Фронтенд переподключается через 3 секунды после нештатного закрытия. Действие
`check_desync` реализовано на сервере, но текущий клиент его не вызывает — задел
на будущую кнопку «синхронизироваться со мной».

## Как работает синхронизация

Владелец — источник истины, его клиент не слушает рассылку `player_state_updated`,
чтобы не зациклиться на своих же событиях.

1. Владелец жмёт play/pause или двигает скраббер → `PUT /player/state` → запись в Redis
   → рассылка `player_state_updated` по комнате.
2. Гость получает состояние: расхождение больше **2 с** → жёсткий `seek`.
3. Если видео и аудио идут разными потоками, мастер-клок — аудио; если `video.currentTime`
   отстаёт больше чем на **0.3 с** — видео догоняет аудио.
4. `player_state_updated` в клиенте применяется только у не-владельцев.

## Тесты

```bash
pip install -r requirements.txt
pytest
```

Покрыты API-роуты (`test_api_*`), репозитории (`test_*_repo.py`), плеер и поиск.
Тесты `test_player.py` и `test_web_search.py` ходят в сеть (YouTube) и качают реальный
фрагмент — им нужен установленный `ffmpeg` и стабильное соединение.

## Деплой

**Render** — `render.yaml` из корня, два сервиса:

- `sync-player-api` — `pip install -r requirements.txt` + `uvicorn app.app:app`,
  переменные `PYTHON_VERSION`, `CORS_ORIGINS`, `BOT_TOKEN`;
- `sync-player-frontend` — static site, `npm run build` из `frontend/`, публикация `dist`.

> В `render.yaml` в `startCommand` указан `app.main:app`, а приложение лежит в `app/app.py`
> (`app.app:app`) — поправьте при деплое.

**Docker / nginx** — `frontend/Dockerfile` собирает Vite и раздаёт статику через nginx,
который проксирует `/api/` на контейнер `api:8000` с поддержкой WebSocket (`Upgrade`).

**Vercel** — фронтенд статикой, `frontend/vercel.json` проксирует `/api/*` на удалённый
backend; поправьте адрес в `destination` под свой хост.

## Безопасность

- `.env` **не должен** попадать в git: в нём лежит токен бота, а `.gitignore` в корне
  репозитория вообще нет. Если файл уже в истории — смените токен через
  [@BotFather](https://t.me/BotFather), добавьте `.env`, `app.db` и `__pycache__/` в
  `.gitignore` и почистите историю.
- Эндпоинты `/api/player/stream` и `/api/player/download` выполняют произвольные URL
  от имени сервера (SSRF-риск). Для публичного инстанса добавьте allowlist доменов в
  `app/api/routes/player.py`.
- `app.db` тоже лежит в репозитории — в проде смонтируйте его на диск или переходите
  на PostgreSQL.
