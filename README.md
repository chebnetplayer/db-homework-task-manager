### Приложение task_manager 

Главные компоненты <br/>
БД: mongodb <br/>
Сервер: fastapi <br/>

Приложение позволяет работать с объектом Task, состоящий из следующих полей <br/>
* title: str - заголовок
* description: str - описание
* assigned_to: str - исполнитель
* created_date: datetime - дата создания
* completed_date: datetime = дата исполнения
* due_date: datetime - планируемая дата исполнения
* files: list[str] - Список id файлов 

Также приложение использует авторизацию mongodb <br/>
При инициализации БД создаются роли tasks_reader, tasks_writer <br/>
Регистрировать новых пользователей может только администратор <br/>

### Методы 

* GET /tasks
*Получить список всех задач*
* POST /tasks
*Создание задачи*
* GET /tasks/{task_id}
*Получить задачу по id*
* PUT /tasks/{task_id}
*Завершить задачу*
* DELETE /tasks/{task_id}
*Удалить задачу*
* POST /tasks/{task_id}/upload
*Прикрепить файл к задаче*
* GET /tasks/download/{id}
*Скачать файл*
* POST /register
*Регистрация пользователя*
* GET /users
*Получить список пользователей*
* GET/tasks/aggregate/{field}
*Получить аггрегированнй список задач по полю*
* GET/tasks/sort/{field}
*Получить отсортированный список задач по полю*
* GET/tasks/search
*Поиск по полю title(текстовый указатель)*
### Поднять приложение локально
```
docker-compose up --build --force-recreate
```



