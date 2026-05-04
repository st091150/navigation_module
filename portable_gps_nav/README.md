# portable_gps_nav

Минимальный набор функций: **расстояние между двумя точками GPS** (градусы WGS84) и **угол поворота к цели**. Не требует установки всего репозитория `navigation_module` — достаточно скопировать эту папку.

## Что внутри

| Функция | Зачем |
|--------|--------|
| `gps_distance_meters(lat1, lon1, lat2, lon2)` | Расстояние по поверхности Земли (м), гаверсинус |
| `distance_to_target((lat, lon), (lat, lon))` | То же через кортежи «робот → цель» |
| `bearing_to_target((lat, lon), (lat, lon))` | Пеленг на цель в **радианах** (конвенция как в основном модуле: ось x на восток) |
| `angle_error(yaw_rad, bearing_rad)` | На сколько повернуться: `bearing − yaw`, свёрнуто в (-π, π] |
| `turn_angle_to_goal_rad(yaw, lat_r, lon_r, lat_g, lon_g)` | Один вызов: yaw робота + координаты → нужный поворот |

Также доступны `bearing_between_points`, `normalize_angle` — как в основном проекте.

Зависимости: только стандартная библиотека Python (`math`).

## Как подключить

**Вариант 1 — папка лежит рядом с вашим проектом.** Добавьте родительский каталог в `PYTHONPATH` или в коде:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # родитель portable_gps_nav

from portable_gps_nav import distance_to_target, bearing_to_target, angle_error
```

**Вариант 2 — только один файл.** Скопируйте только `simple_gps_nav.py` в свой проект и импортируйте:

```python
from simple_gps_nav import distance_to_target, turn_angle_to_goal_rad
```

## Пример

```python
import math

robot_lat, robot_lon = 52.520008, 13.404954
goal_lat, goal_lon = 52.520208, 13.404954
current_yaw_rad = 0.0  # ваш ориентир должен быть в той же системе, что и bearing_to_target

d = distance_to_target((robot_lat, robot_lon), (goal_lat, goal_lon))
bearing = bearing_to_target((robot_lat, robot_lon), (goal_lat, goal_lon))
turn = angle_error(current_yaw_rad, bearing)

print(f"Расстояние: {d:.2f} м")
print(f"Поворот: {math.degrees(turn):.2f}°")
```

Формулы совпадают с `navigation_module.core` — при изменении алгоритма в основном пакете имеет смысл обновить и этот файл вручную.
