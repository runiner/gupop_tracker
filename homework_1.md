# Event Storming трекера задач Попугов

### Notes:
1. "Login -> UserLoggedIn" как будто ничего не меняют в системе, т.е. похоже на Query
2. "CreateTask -> TasksReassigned" выглядит как ситуативное решение, сейчас его достаточно, но может быть лучше было бы Accounter научить понимать событие TaskCreated
3. Tracker дублирует список пользователей из HR, он нужен Tracker'у для возможности назначения задач на новых пользователей
4. Получилось, что на диаграмме EventStorming не особо нужны Query запросы (например просмотр аналитики/статистики). Это может быть неправильно, т.к. можно просмотреть "сложный" Query, объединяющий разные сущности из разных мест.


![Event Storming Diagram](homework_1_event_storming.drawio.svg "Event Storming Diagram for popug tracker")

