# restaurant-chat-bot
## Description
Simple chat bot MVP based on [python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/index.html) library.
It can gather info about number of people and the time for booking.
It does not include database integration for now.
## How to run
```
docker build . -t tgbot
docker run -e API_KEY={YOUR_API_KEY} tgbot
```
## Testing
For testing [telethon](https://pypi.org/project/Telethon/) library could be used. However automated tests are out of the scope
of this basic project.
