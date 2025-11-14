# 💱 ValutaTrade Hub

██╗ ██╗ █████╗ ██╗ ██╗ ██╗████████╗ █████╗ ████████╗██████╗ ██████╗ ███████╗
██║ ██║██╔══██╗██║ ██║ ██║╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝
██║ ██║███████║██║ ██║ ██║ ██║ ███████║ ██║ ██████╔╝██████╔╝█████╗
██║ ██║██╔══██║██║ ██║ ██║ ██║ ██╔══██║ ██║ ██╔══██╗██╔═══╝ ██╔══╝
╚██████╔╝██║ ██║███████╗╚██████╔╝ ██║ ██║ ██║ ██║ ██║ ██║██║ ███████╗
╚═════╝ ╚═╝ ╚═╝╚══════╝ ╚═════╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝╚═╝ ╚══════╝

php-template
Копировать код

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Poetry-managed-60a5fa.svg" alt="Poetry">
  <img src="https://img.shields.io/badge/Lint-Ruff-brightgreen.svg" alt="Ruff">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version">
</p>

> **ValutaTrade Hub** — CLI-приложение для управления валютным портфелем.  
> Реализует регистрацию, покупку и продажу валют, обновление курсов из внешних API, хранение портфеля и логирование операций.  
> Основано на принципах **чистой архитектуры** с чётким разделением слоёв `core`, `infra`, `cli` и `parser_service`.

🎥 **Демонстрационное видео:** *[https://asciinema.org/a/iYqOKUoGRmE0f29BHAxwTtT0D]*

---

## 🏗️ Архитектура проекта
```
finalproject_Nosulchak_dpo_nod/
│  
├── data/                           # Хранилище данных
│    ├── users.json                 # Пользователи системы
│    ├── portfolios.json            # Портфели пользователей  
│    └── rates.json                 # Кэш текущих курсов валют
│
├── valutatrade_hub/               # Основной пакет приложения
│    ├── __init__.py
│    ├── logging_config.py         # Настройка логов (формат, уровень, ротация)
│    ├── decorators.py             # @log_action (логирование операций)
│    ├── core/                     # Ядро приложения - бизнес-логика
│    │    ├── __init__.py
│    │    ├── currencies.py        # Базовый класс Currency и наследники Fiat/Crypto
│    │    ├── exceptions.py        # Пользовательские исключения
│    │    ├── models.py            # Модели данных (User, Wallet, Portfolio)
│    │    ├── usecases.py          # Бизнес-сценарии с исключениями и логированием
│    │    └── utils.py             # Вспомогательные функции (валидация, конвертация)
│    ├── infra/                    # Инфраструктурный слой
│    │    ├─ __init__.py
│    │    ├── settings.py          # Singleton SettingsLoader (конфигурация)
│    │    └── database.py          # Singleton DatabaseManager (абстракция над JSON)
│    ├── parser_service/           # Сервис парсинга курсов валют
│    │    ├── __init__.py
│    │    ├── config.py            # Конфигурация API и параметров
│    │    ├── api_clients.py       # Клиенты внешних API (ExchangeRate-API)
│    │    ├── updater.py           # Логика обновления и кэширования курсов
│    │    └── storage.py           # Работа с историческими данными
│    └── cli/                      # Командный интерфейс
│         ├─ __init__.py
│         └─ interface.py          # Интерактивный CLI
│
├── main.py                        # Точка входа в приложение
├── Makefile                       # Автоматизация задач
├── poetry.lock                    # Poetry lock-файл
├── pyproject.toml                 # Конфигурация проекта и зависимости
├── README.md                      # Документация проекта
└── .gitignore                     # Игнорируемые файлы Git
```
Ключевые особенности архитектуры:
🏗️ Слоистая архитектура:
core/ - Чистая бизнес-логика

infra/ - Инфраструктурные concerns

parser_service/ - Внешние интеграции

cli/ - Презентационный слой

🔧 Принципы проектирования:
Singleton для настроек и БД

Декораторы для cross-cutting concerns

Исключения для обработки ошибок

Абстракция над хранилищем

📁 Данные:
JSON файлы для persistent storage

Разделение текущих и исторических данных

Логирование операций в отдельный файл
---
```
## ⚙️ Установка и запуск
```
bash
# 1. Установка зависимостей
```
poetry install
```
# 2. Запуск CLI
```
poetry run project
```
# 3. Справка по командам
```
poetry run project --help
```
🧩 Основные команды CLI
```
Команда	Аргументы	Описание
register	--username, --password	Регистрация нового пользователя
login	--username, --password	Вход в систему
show-portfolio	--base USD	Просмотр портфеля
buy	--currency BTC, --amount 0.1	Покупка валюты
sell	--currency BTC, --amount 0.1	Продажа валюты
get-rate	--from_currency USD, --to_currency EUR	Получение курса
update-rates	(опционально) --source	Обновление курсов
```
🧠 Примеры использования
```
# Регистрация
```
 register --username alice --password 12345
```
# Вход
```
 login --username alice --password 12345
```
# Покупка
```
 buy --currency BTC --amount 0.05
```
# Просмотр портфеля
```
 show-portfolio --base USD
```
# Проверка курса
```
 get-rate --from_currency USD --to_currency EUR
```
# Продажа
```
 sell --currency BTC --amount 0.02
```
# Обновление курсов
```
 update-rates
```
🧱 Логирование
```
Файл логов: logs/actions.log
```
sql

INFO 2025-11-11T12:45:22 BUY user='alice' currency='BTC' amount=0.0500 rate=59300.00 base='USD' result=OK
INFO 2025-11-11T12:48:14 SELL user='alice' currency='BTC' amount=0.0200 rate=60000.00 base='USD' result=OK
```
🚨 Обработка ошибок
```
Исключение	Где возникает	Пример
InsufficientFundsError	Продажа без средств	«Недостаточно средств: доступно 0.01 BTC, требуется 0.05 BTC»
CurrencyNotFoundError	Неизвестный код валюты	«Неизвестная валюта 'XYZ'»
ApiRequestError	Ошибка API при обновлении курсов	«Ошибка при обращении к внешнему API: 429 Too Many Requests»
```
⚙️ Конфигурация (SettingsLoader)
```
toml
Копировать код
[tool.valutatrade]
data_path = "data/"
logs_path = "logs/"
rates_ttl_seconds = 3600
base_currency = "USD"
```
🧰 Makefile цели
```
Цель	Описание
make install	Установка зависимостей
make lint	Проверка кода Ruff
make project	Запуск CLI
make build	Сборка пакета
make publish	Публикация
```
🧩 Технологии

🐍 Python 3.10+

📦 Poetry

🧹 Ruff

📊 PrettyTable

🌍 ExchangeRate API

💾 JSON-хранилище

👑 Автор
Проект создан в рамках курса
“Архитектура Python-приложений (DPO НОД)”

Автор: Nosulchak
Год: 2025



