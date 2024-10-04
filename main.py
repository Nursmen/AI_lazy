from telethon import TelegramClient
import datetime

import openai
import dotenv
import os

API_ID = 10221683     
API_HASH = '4fde13d8d9e62daad1b89800a67ebed6' 
client = TelegramClient('my-client', API_ID, API_HASH)

dotenv.load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_client = openai.OpenAI()

now = datetime.datetime.now(datetime.timezone.utc)
monday = now - datetime.timedelta(days=now.weekday())

def is_digest(message):
    if '#дайджест' in message.text:
        return True
    return False

def summarize(request):
    
    prompt = f"""На входе - текст, на выходе - суммаризация в 2 предложения, где 1 - описание из 1-3 слов, а 2 - интересный факт. 
    
    Пример входа:
    Машина это движущееся средство передвижения которое люди часто используют.

    Пример выхода:
    Машина. Средство, которое люди часто используют

    Твой вход:    
    {request}\n\n"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and print the generated response
    generated_text = response.choices[0].message.content
    return generated_text

def group(texts):
    texts = '\n'.join(texts)

    prompt = f'''
        Пример входа:
        Коты орудуют в городе.
        Собаки наподают.
        Машины не работают.

        Пример выхода:
        **Животные бушуют**
        - Коты орудуют в городе.
        - Собаки наподают.
        **Техника ломается**
        - Машины не работают.

        Твой вход:
        {texts}
    '''

    response = openai_client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Твоя задача сгрупировать данные"},
            {"role": "user", "content": prompt}
        ]
    )

    generated_text = response.choices[0].message.content
    return generated_text

async def main(parse_ch = -1001466120158, send_ch = -1001968237320):

    results = []
    channel_name = await client.get_entity(parse_ch)
    channel_name = channel_name.username

    async for message in client.iter_messages(parse_ch, limit=25):
        if message.text != '' and message.date >= monday and not is_digest(message):

            summarized = summarize(message.text).split('.')
            summarized[0] = f"[{summarized[0]}](https://t.me/{channel_name}/{message.id})"

            summarized = '.'.join(summarized)

            results.append(summarized)
            print(summarized)

    grouped = group(results)
    await client.send_message(send_ch, grouped)


with client:
    try:
        parse_ch = int(input('Channel we want to parse: '))
        send_ch = int(input('Channel we want to send to: '))
    except:
        parse_ch = 0
        send_ch = 0

    if parse_ch != 0 and send_ch != 0:
        client.loop.run_until_complete(main(parse_ch, send_ch))
    else:
        client.loop.run_until_complete(main())