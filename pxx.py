import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler
import os
from telegram import InputMediaPhoto
import get_url
import config
import traverse_img

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
CHOU = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["抽！"]]
    await update.message.reply_text("I'm a bot, please sent me 1024 link or just 抽！",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="9 pics one time"
        ),
    )
    return CHOU
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please sent me 1024 link")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in [1905615710, 910241302]:
        logging.info('-'.join((str(update.effective_chat.id),'unauthed_one',url)))
        await context.bot.send_message(chat_id=update.effective_chat.id, text='爬取功能暂不对外开放')
    try:
        url = update.message.text
        logging.info('-'.join((str(update.effective_chat.id),url)))
        if url == "抽！":
            pic_list = []
            result = traverse_img.rows_nub()
            logging.info('-'.join((str(update.effective_chat.id),'抽了一次')))
            for pic in result:
                pic_list.append(InputMediaPhoto(open(pic[0], 'rb'), caption = 'enjoy'))
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=pic_list)
        
        else:
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
    logging.info('-'.join((str(update.effective_chat.id),'抽了一次')))
    for pic in result:
        pic_list.append(InputMediaPhoto(open(pic[0], 'rb'), caption = os.path.basename(os.path.dirname(pic[0]))))
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':

    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOU: [CommandHandler("show", show_at_random)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    send_1024_pic = CommandHandler('show',show_at_random)
    list_img = CommandHandler('list',list_img_db)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(send_1024_pic)
    application.add_handler(list_img)
    application.run_polling()