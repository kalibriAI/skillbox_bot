### Предстоящие обновления

- Добавить анотации типов [9.8.2023] :white_check_mark:
- Добавить первую регистрацию профиля и ввод ключа апи, затем сохранить ключ в базу.
- Добавить команду для изменения ключа апи.
- Поставить систему дурако устойчивости (проверка вводимых значений при поиске отеля и различные обработчики исключений).
- Доделать систему записи выбранного отеля в базу данных.
- Добавить возможность просмотра всех фото в дургом сервисе (не обязательно).
- Сделать так чтоб если юзер ввел город то отправляло найденные отели, а если страну то города на этапе ввода местоположения.
- Сделать удаление сообщений ввода данных дабы не засорять чат.
- Сделать проверку чтоб максимальное значение бюджета было больше чем минимальное.
- Добавить кнопку завершить поиск, чтоб поиск не заканчивался после выбора одного отеля.
##### Первый релиз выйдет после закрытия выше перечисленных обновлений

### Установка зависимостей
```terminal
pip install requirements.txt
```


### Запуск
- Переименовать файл: bot.ini.template -> bot.ini
- Создать базу данных ПосгреСКЛ
- Заполнить bot.ini своими данными
- Запустить файл cli.py

### База данных
Для работы бота вам нужно вручную выполнить следуюзие запросы в вашей базе:

```create table users (id int primary key, key text);```

```create table hotels (id serial primary key, owner int, hotel_id int, data json);```

