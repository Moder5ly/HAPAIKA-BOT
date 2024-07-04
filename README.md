## Хапайка няшок


![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)<br> [![Support Group!](https://img.shields.io/badge/Join%20Group-↗-green)](https://t.me/hurtivka)


## Як додавати няшок до бота?

#### Формат: 
```
/upload посилання_на_картинку ім'я-няшки назва-аніме рідкість
```
Приклад використання: 
```
/upload посилання_на_картинку mahiro-oyama мій-братик-вже-не-братик! 4
```
Рідкості наступні:

| Код    | Рідкість      |
| ------ | ------------- |
| 1      | ⚪️ Звичайна   |
| 2      | 🟣 Рідкісна   |
| 3      | 🟡 Легендарна |
| 4      | 🔴 Міфічна    |

## Команди для користувачів
- `/ping` - перевірити час швидкодії бота
- `/guess` - вгадати няшку
- `/fav` - встановити няшку як улюблену
- `/trade` - обмінятися няшками
- `/gift` - подарувати няшку комусь
- `/collection` - показати свій гарем няшок
- `/ctop` - глянути топ збирачів гарему у вашому чаті
- `/changetime` - змінити частоту появи няшок
  
## Команди для адмінів
- `/upload` - додати нову няшку до бази даних
- `/delete` - видалити няшку з бази даних
- `/update` - оновити значення няшки в базі даних

## Команди для власника
- `/stats` - Lists number or groups and users
- `/list` - Sends a document with list of all users that used the bot
- `/groups` - Sends a document with list of all groups that the bot has been in

## Способи встановлення

### Heroku
- Форкнути репозиторій.
- Заповнити всі змінні у [`config.py`](./shivu/config.py).
- Перейти до Heroku та задеплоїти репозиторій.

### Local Deploy/VPS
- Заповнити всі змінні у [`config.py`](./shivu/config.py).
- Відкрити термінал вашого VPS (у нашому випадку, на базі Debian) та запустити наступну інструкцію:
```bash
sudo apt-get update && sudo apt-get upgrade -y           

sudo apt-get install python3-pip -y          
sudo pip3 install -U pip

git clone https://github.com/<YourUsername>/WAIFU-HUSBANDO-CATCHER && cd WAIFU-HUSBANDO-CATCHER

pip3 install -U -r requirements.txt          

sudo apt install tmux && tmux          
python3 -m shivu
```       

## Поради розробника
- Не користуватися Heroku. Хіба що для тестування. Інакше інлайн працюватиме повільно.
- Користуватися надійним VPS-провайдером.
