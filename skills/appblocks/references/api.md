# AppBlocks Cloud HTTP API (по appblocks.io/docs/cloud/api/*, октябрь 2026)

Пересказ официальной документации (страницы: api, account, projects, devices, device-groups, workspaces,
dashboards, workflows, integrations). При расхождении верь свежей странице документации.

## Основное
- **База:** `https://api.appblocks.io` (не app.appblocks.io; self-hosted — свой URL).
- **Ключ:** `abk_…` (32 байта), создаётся в веб-приложении Settings → API Keys. Заголовок `x-api-key: abk_…`
  или `Authorization: Bearer abk_…`. Действует как пользователь (его workspaces/tenants/устройства).
- **Скоупы:** `read` (GET/HEAD/OPTIONS, всегда) и `write` (POST/PUT/PATCH/DELETE). Без write → `403 {"message":"This API key does not have the write scope"}`.
- `GET /api/me` → `{id, email, auth:"apiKey", apiKey:{id,name,scopes}}`. Проверяй первым делом.
- `/api/account/*` ключом недоступно (только сессия): ключ не меняет пароли и не создаёт ключи.
- Срок ключа 1–365 дней или бессрочно; до 25 активных; отзыв мгновенный (`401 Invalid or expired API key`).
- **Пагинация:** `start` (0), `count` (10; логи/метрики 20) → `{count: <всего>, data:[…]}`, сортировка по updatedAt ↓.
- `search=<текст>` — по имени. Фильтры полей `<field>___eq|ne|gt|lt|gte|lte=<v>` (пусто = null).
- Время логов/метрик: `startTime`, `endTime` ISO 8601 (по умолчанию последние 24 ч).
- Область: без `workspace` — личное; `workspace=<id>`; `tenant=<id>`.
- Ошибки: 400 (нет/невидимо), 401, 403 (роль/скоуп), 404, 500, 503 (не настроена интеграция). Тела ошибок разнородны — любой не-2xx = ошибка.
- Роли workspace: owner, admin, operator (устройства только чтение, проекты править может), member. Tenant: admin, member.
- Устройства этим API не пользуются: они ходят по MQTT (deviceId + key); по HTTP — только скачивание OTA.

## Замечено на практике (октябрь 2026)
- `GET /api/projects/examples` и `/examples/categories` отвечали 500 (с ключом и без) — примеры брать с `https://appblocks.io/projects/<имя>.json`.
- `GET /api/projects/:id` отдаёт проект целиком, `device` строкой (`"TPP2W(G2)"`).
- `POST /api/projects/code` работает и с ключом; для `tios` возвращает TIDE-проект (см. generated-code.md).
- `POST /api/projects/build` (без ключа): тело `{command:"build", files:<ответ /api/projects/code>, project:{runtime, device},
  debug:true}` → компилятор TIDE Tibbo. Успех: HTTP 200, `status:"completed"`, `tpc`/`binary`/`pdb` как `{type:"Buffer", data:[…]}`.
  Ошибка компиляции: HTTP 500 и `output` с текстом компилятора (`file.tbs(N): error C1013: …`). Обёртка - `ab_api.py build`.
  Предупреждения `C1006 preprocessor redefinition` идут из шаблона фреймворка и норма.
- Ключ API бывает **только с read**: `ab_api.py me` покажет `scopes`; на запись сервер отвечает 403
  «This API key does not have the write scope» - попроси пользователя выпустить ключ с write.
- Веб-приложение под входом пользователя ходит в тот же API с куки сессии (`/api/me` → `"auth":"session"`); из встроенного
  браузера можно читать проекты так же, как ключом, но писать - только с подтверждения пользователя на конкретный вызов.
- После `update` проекта, открытого в редакторе, попроси перезагрузить вкладку без сохранения: иначе редактор
  перезапишет облачную версию своей.

## Без авторизации
`GET /api/projects/examples`, `/examples/categories`, `/examples/:id` (с README и полным `project`) ·
`POST /api/projects/code|download|save|blockgen|build` · `GET /api/projects/:id/versions/:vc/firmware/:file` ·
`GET /cgg/public/devices/...` (устройства с publicDashboard) · `ALL /cgg/webhooks/:id` · `GET /api/tibbits/docs/:model`.

## Проекты (`/api/projects`, `/api/tasks`, `/api/workspace-projects`)
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/projects` | Список (`start,count,search,workspace`, фильтры). **Узлы `node_*` из списка вырезаны** |
| GET | `/api/projects/:id` | Один проект целиком: `{count:0, data:[project]}` |
| POST | `/api/projects` | Создать. Тело: `name, description, shortDescription, device{platform,name}, features, featureFlags, featureFlagMap, version, runtime ("tios"\|"zephyr"), workspace` |
| PUT | `/api/projects/:id` | Обновить (те же поля; workspace/владелец не меняются) |
| DELETE | `/api/projects/:id` · `/api/projects` (`{projects:[ids]}`, всё или ничего) | Удалить |
| POST | `/api/projects/code` | `{params:{project, debug:true}}` → `[{name, contents}]` — **исходники прошивки** |
| POST | `/api/projects/download` (= `/save`) | тело = сам проект → ZIP с исходниками (для tios — с файлами платформы) |
| POST | `/api/projects/blockgen` | `{prompt, project}` → сгенерированные ИИ блоки (JSON) |
| POST | `/api/tasks` | Сборка в очередь: `{command:"build", files:[{name,contents}], project{runtime,device}, debug, requireSymbols}` → `{status:"running", output:{puuid}}` |
| GET | `/api/tasks/:id` | Статус: running (progress) / completed (`binary, symbols, hex`) / aborted (ошибка компиляции, `output`) / unknown. Задача живёт 3 мин — опрашивай сразу |
| DELETE | `/api/tasks/:id` | Отменить |
| POST | `/api/projects/build` | Синхронная сборка (для инструментов): `tpc, pdb, binary, hex, symbols, output` |
| GET | `/api/projects/:id/versions[/:_id]` | Версии (`versionCode, versionDescription, url, releaseUrl…`). В get по одной — `_id` версии |
| POST | `/api/projects/:id/versions` | Создать версию (`versionCode` уникален, + поля проекта) |
| PUT | `/api/projects/:id/versions/:versionCode` | multipart: `binary` (обяз.), `releaseBinary`, `firmwareVersion`, `runtime` → 204; URL `.tcu` (OTA) и `.bin` |
| DELETE | `/api/projects/:id/versions/:_id` | Удалить версию |
| GET | `…/versions/:vc/firmware/:file` (.tcu) · `…/release/:file` (.bin) · `…/:file` | Публичные загрузки |
| POST | `/api/workspace-projects/export` | `{workspaceId, bundleVersion, includeBinaries}` → JSON-бандл (projects, projectVersions, deviceGroups, workflows, pageApps, scadaScreens; значения переменных workspace заменены заглушкой) |
| POST | `/api/workspace-projects/import` | `{bundle, workspaceName, workspaceId?}` — новые ID, ссылки сохраняются |
| POST | `/api/workspace-projects/update` | `{bundle, workspaceId, removeOrphans}` — обновление по `_bundleSourceId` |

Runtime: `tios` → сборка Tibbo BASIC/TiOS, результат `.tpc`/`.pdb` (как TIDE); `zephyr` → Zephyr C.
Редактор открывает проект по ссылке: `https://app.appblocks.io/app/project/new?url=<URL на project JSON>`.

## Устройства (`/cgg/devices`; `:id` = deviceId)
GET список (`workspace, tenant, group, devices, search`, фильтры напр. `state.connected___eq=true`) ·
POST регистрация `{name, workspace?, tenant?}` → deviceId + key (MQTT) · GET/PUT(`name,tags,publicDashboard`)/DELETE `/:id` ·
GET `/:id/config` (что объявило приложение) · POST `/:id/system/:command` ·
GET/DELETE `/:id/logs`, GET `/logs` (по парку), GET `/:id/metrics`, `/metrics` ·
GET `/:id/variables[/:var]`, POST `/:id/variables/:var` `{value}` (ставится в очередь, не мгновенно), GET `…/:var/changes`, DELETE `/:id/variables/changes` ·
GET `/:id/tables/:t` (CSV), `/count`, `/changes`; POST `/:id/tables/:t/changes` `{action:"insert", row:{…}}` или `{action:"import", data:"csv"}`; DELETE `/:id/tables/changes` ·
POST `/:id/commands/:cmd` `{data}` → MQTT `devices/<id>/commands/<cmd>` ·
POST `/:id/firmware` `{url: <url версии .tcu>, workspaceId}` (OTA), DELETE `/:id/firmware/changes`.
Объект устройства: `deviceId, key, name, workspace, tenant, group, tags, publicDashboard, config{variables,tables}, state{connected, firmwareVersion, appId, appVersion, appName, mac, ip, bootTime, timezone, variables, tables}, changes{variables,tables,firmware}`.
Логи и метрики хранятся 3 недели, прогоны workflow — 3 дня.

## Группы устройств (`/cgg/groups`)
GET (`workspace, tenant, search`) · POST `{name, workspace?, tenant?, project?, version?}` · GET/PUT(`name, project, version` — перепривязка к версии с согласованием stg/tbl)/DELETE `/:id` ·
POST `/:id/devices` `{devices:[_id]}` · DELETE `/:id/devices/:deviceId` · POST `/:id/firmware` `{versionId}` (OTA всей группе) ·
POST `/:id/variables` `{variables:[{variable,value}]}` · POST `/:id/tables` `{name,data,action}` · DELETE `/:id/tables/:name`.

## Workspaces и tenants (`/api/workspaces`)
GET список / GET `/:id` / POST `{name}` / PUT `{name}` / DELETE `{confirmName}` (удаляет ВСЁ) ·
users: POST `{email,role}`, PUT `/users/:uid/role`, DELETE · invites: POST/GET/DELETE ·
variables: GET, PUT `{variables:{…}}` (заменяет целиком) · tenant-variable-templates GET/PUT · audit-logs GET (`tenant, limit≤200, skip`) ·
tenants: `/:ws/tenants[/:tid]` CRUD, `/variables`, `/users`, `/invites`.

## Облачные workflow (`/cgg/workflows`, `/cgg/webhooks/:id`)
CRUD; POST `{name, trigger, nodes, workspace}` всегда создаёт выключенным (`enabled:false`), включать PUT `{enabled:true}` ·
GET `/:id/runs`. Триггеры: `Time` (cron), `Webhook` (`properties.url`), `DeviceEvent`, `DeviceUpdate` (`filter: device|group|any`).
**Всегда задавай `properties.condition: {rules:[]}`** — без него workflow молча не запускается.
Узлы по порядку: `Condition`, `HTTPCall {url,method,data,headers[]}`, `Email {recipient[], subject, body}`,
`DeviceAction {device|device_id, action:set_variable|execute_command, variable|command, data}`, `CustomFunction {language:"javascript", code}`.
Выражения `{{ data… }}`, `{{ input… }}`, `{{ workspace.variables… }}`, `{{ tenant.variables… }}`. `retrigger:false` — после первого срабатывания отключается.

## Дашборды, SCADA, источники данных
`/cgg/pages` (дашборды: pages[components, queries], scripts, import `{bundle:{_type:"dashboard",data}}`, homepage) ·
`/cgg/scada` (screens[elements, connections], tagBindings, alarmLimits; import `_type:"scada"`; `/binding/devices`) ·
`/cgg/datasources` (личные; типы MySQL, mongodb, restapi, Devices, DeviceEvents; **properties хранят пароли — не выгружай**).

## Маркетплейс плагинов
`GET /cgg/extensions` → `{data:[{_id, name, summary, author, status (approved | pending), version, features:[custom_feature…]}], count}`,
`GET /cgg/extensions/:id` - один плагин целиком (формат format.md §5). Чтение - ключом с правом read.

## Интеграции
ИИ-ассистент Cody (CopilotKit, `/api/copilotkit/*`) — только поиск по документации, редактирование проектов внешним клиентам недоступно; MCP нет.
`GET /api/tibbits/docs/:model` — прокси страниц docs.tibbo.com по Tibbit (`00_3` → tibbit_00-3).
TIDE remote: `/tide/client/list`, `/tide/client/remotedevices/:mac` (+ `settarget` бронь на 10 мин).

## Правила работы с API в скилле
- Ключ только из окружения (`APPBLOCKS_API_KEY`); не печатать, не сохранять.
- Чтение — свободно. Любая запись (POST/PUT/DELETE: проекты, устройства, переменные, команды, OTA, workflow,
  удаление) — только после явного «да» пользователя на конкретный запрос; показывай метод, путь и тело заранее.
- Особо опасно: DELETE workspace, OTA-прошивка устройств/групп, команды устройствам, PUT переменных на живых устройствах.
