# АптекаПлюс для Visual Studio

Это Flask-приложение оформлено как Python-проект Visual Studio: есть файл решения `PharmacyPlus.sln` и проект `PharmacyPlus.pyproj`.

## Что должно быть установлено

1. Visual Studio 2022.
2. Workload `Python development` в Visual Studio Installer.
3. Python 3.12 или совместимая версия.
4. MongoDB Community Server для настоящей базы данных.
5. MongoDB Compass для просмотра базы.

Важно: MongoDB Compass - это только графический интерфейс. Он не запускает сервер базы. Приложению нужен именно MongoDB Community Server или другой запущенный MongoDB-сервер.

## Как открыть проект

1. Запустите Visual Studio.
2. Выберите `Open a project or solution`.
3. Откройте файл `PharmacyPlus.sln`.
4. В Solution Explorer должен появиться проект `PharmacyPlus`.

## Первичная настройка

Откройте `View > Terminal` или `Tools > Command Line > Developer PowerShell` в Visual Studio и выполните из папки проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

В Visual Studio выберите созданное окружение `.venv` как интерпретатор проекта, если Visual Studio не выбрала его автоматически.

## Настройки MongoDB

Файл `.env` должен содержать:

```text
SECRET_KEY=change-me
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=pharmacy_db
PORT=5000
FLASK_DEBUG=1
USE_MOCK_DB=0
```

Если MongoDB Community Server установлен локально и запущен, приложение подключится к `mongodb://localhost:27017/`.

В MongoDB Compass подключайтесь к той же строке:

```text
mongodb://localhost:27017/
```

После первого запуска приложения и открытия `/seed` в Compass появится база `pharmacy_db` с коллекциями `medications` и `sales`.

## Запуск приложения

Вариант 1: нажмите `Start` / `F5` в Visual Studio.

Вариант 2: запустите из терминала:

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Откройте в браузере:

```text
http://localhost:5000/seed
http://localhost:5000
```

`/seed` заполняет базу тестовыми медикаментами и продажами.

## Если MongoDB Server еще не установлен

Для временной проверки интерфейса можно в `.env` поставить:

```text
USE_MOCK_DB=1
```

Так приложение запустится без MongoDB, но данные будут храниться только в памяти и исчезнут после остановки приложения.

## Структура проекта

```text
PharmacyPlus.sln
PharmacyPlus.pyproj
run.py
requirements.txt
.env.example
app/
  __init__.py
  config.py
  constants.py
  db.py
  routes/
    dashboard.py
    medications.py
    sales.py
    forecast.py
  templates/
    base.html
    dashboard.html
    forecast.html
    medications/
    sales/
  static/
    css/
      styles.css
```
