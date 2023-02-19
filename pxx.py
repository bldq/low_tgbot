import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
from telegram import InputMediaPhoto
import get_url
import config
import traverse_img

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please sent me 1024 link")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in [1905615710, 910241302]:
        logging.info('-'.join((str(update.effective_chat.id),'unauthed_one',url)))
        await context.bot.send_message(chat_id=update.effective_chat.id, text='爬取功能暂不对外开放')
    try:
        url = update.message.text
        logging.info('-'.join((str(update.effective_chat.id),url)))
        if 'mob' in url:
            url = url.replace('mob','data')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(get_url.get_1024_url(str(url))))
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Bad link')
    except AttributeError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Bad or Blank link')

async def show_at_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pic_list = []
    result = traverse_img.rows_nub()
    for pic in result:
        pic_list.append(InputMediaPhoto(open(pic[1], 'rb'), caption = pic[2]))
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=pic_list)
        # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic, 'rb'))

async def list_img_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in [1905615710, 910241302]:
        logging.info('-'.join((str(update.effective_chat.id),'unauthed_one')))
        await context.bot.send_message(chat_id=update.effective_chat.id, text='此功能仅限管理员')
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=traverse_img.reset_media_db())
    except ValueError:
        pass


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    send_1024_pic = CommandHandler('show',show_at_random)
    list_img = CommandHandler('list',list_img_db)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(send_1024_pic)
    application.add_handler(list_img)
    application.run_polling()