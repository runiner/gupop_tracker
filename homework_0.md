# Черновик архитектуры трекера задач Попугов

## Набор сервисов
1. HR: расширенный профиль сотрудников, информация о ролях, изменения сотрудников (смена роли, добавление/удаление сотрудника)
2. Tracker: учет задач, назначение/переназначение, регистрация выполнения 
3. Accounter: стоимость задач, доходы/расходы сотрудников
4. Dashik: Обсчет аналитики, обновление счетчиков

### сервис HR
Отправляет события
* EmployeeUpdated [employee_id, role, state, datetime]

Предоставляет API Создания/Обновления сотрудников 

### сервис Tracker
Отправляет события
* TaskCompleted [task_id, employee_id, datetime]
* TaskCreated (нужно ли?) [task_id, employee_id, datetime]
* TasksReassigned [list[taskid, new_assignee_id], datetime]

Предоставляет API создания, переназначения и закрытия задач

### сервис Accounter
Отправляет события
* BalanceUpdated [employee_id, change, new_balance]

Обновляет балансы сотрудников по TaskCompleted, TasksReassigned

Отдает инфу по сотруднику по API

### сервис Dashik
Не отправляет событий

Обновляет статистику по BalanceUpdated

Отдает статистику по API
