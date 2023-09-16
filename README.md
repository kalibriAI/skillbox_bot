### Предстоящие обновления


- Добавить команду для изменения ключа апи.
- Сделать удаление сообщений ввода данных дабы не засорять чат.
- Добавить кнопку завершить поиск, чтоб поиск не заканчивался после выбора одного отеля.
##### Первый релиз выйдет после закрытия выше перечисленных обновлений

### Установка зависимостей
```terminal
pip install requirements.txt
```


### Запуск
- Создать файл bot.ini
- Заполнить данными
  ```
  [bot]
  token =
  admin_id =

  [db]
  host =
  password =
  user =
  database =
    ```
- Создать базу данных ПосгреСКЛ
- Заполнить bot.ini своими данными
- Запустить файл cli.py

### База данных
Для работы бота вам нужно вручную выполнить следуюзие запросы в вашей базе:

```create table users (id int primary key, key text);```

```create table hotels (id serial primary key, owner int, hotel_id int, data json);```

