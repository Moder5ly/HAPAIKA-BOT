## Хапайка вайфу та хасбендо


![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)<br> [![Support Group!](https://img.shields.io/badge/Join%20Group-↗-green)](https://t.me/hurtivka)


## Як додавати няшок до бота?

Формат: 
```
/upload img_url character-name anime-name rarity-number
```
#### Приклад: 
```
/upload Img_url muzan-kibutsuji Demon-slayer 3
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
- `/topgroups` - List the groups with biggest harem (globally)
- `/top` - List the users with biggest harem (globally)
- `/ctop` - List the users with biggest harem (current chat)
- `/changetime` - змінити частоту появи няшок
  
## Команди для адмінів
- `/upload` - Add a new character to the database 
- `/delete` - Delete a character from the database 
- `/update` - Update stats of a character in the database

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
