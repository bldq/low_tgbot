import logging
import os
import asyncio
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputMediaPhoto
from telegram.ext import (
    filters, 
    MessageHandler, 
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    ConversationHandler
)

# 导入您的自定义模块
import get_url
import config
import traverse_img

# 配置日志记录，方便排查报错和用户请求
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

CHOU = range(1)

# ================= 配置区 =================
# 管理员的 Telegram User ID 列表
ADMIN_IDS = [1905615710, 910241302]

# 创建一个全局的管理员过滤器，用于在路由层直接拦截未授权访问
admin_filter = filters.User(user_id=ADMIN_IDS)
# =========================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令，下发快捷键盘"""
    reply_keyboard = [["抽！"]]
    await update.message.reply_text(
        "I'm a bot, please send me 1024 link or just 抽！",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, input_field_placeholder="9 pics one time"
        ),
    )
    return CHOU


async def chou_logic(chat_id: int, bot):
    """
    抽图的核心业务逻辑，已抽离为独立函数以便多处调用。
    包含核心的 File ID 缓存机制，实现“秒传”和“免流量”。
    """
    pic_list = []
    
    # 1. 使用 asyncio.to_thread 将同步的数据库查询放到后台线程，防止阻塞整个机器人的响应
    result = await asyncio.to_thread(traverse_img.get_random_pics, 9)
    
    if not result:
        await bot.send_message(chat_id=chat_id, text="图库是空的哦，请管理员先使用 /list 同步数据库。")
        return

    logging.info(f"User {chat_id} - 触发抽图一次")
    
    # 2. 组装发送媒体组
    for media_id, path, file_id in result:
        # 获取图片所在的文件夹名称作为图片说明 (Caption)
        caption = os.path.basename(os.path.dirname(path))
        
        if file_id:
            # 【核心优化】：库里有缓存的 file_id，直接传字符串，Telegram内网秒发，不耗费您的服务器流量
            pic_list.append(InputMediaPhoto(media=file_id, caption=caption))
        else:
            # 没有缓存，说明是第一次发送，从本地硬盘读取二进制文件上传
            pic_list.append(InputMediaPhoto(media=open(path, 'rb'), caption=caption))
    
    try:
        # 3. 发送媒体组（Telegram 限制媒体组最多10张）
        messages = await bot.send_media_group(chat_id=chat_id, media=pic_list)
        
        # 4. 提取新上传图片的 File ID 并更新到数据库中
        for i, msg in enumerate(messages):
            media_id, path, file_id = result[i]
            # 如果之前没有 file_id，说明这次是刚上传的，我们需要把它存下来
            if not file_id:
                # msg.photo 是一个列表，包含不同清晰度的图片，[-1] 代表最高清晰度的 file_id
                new_file_id = msg.photo[-1].file_id
                # 扔到后台线程去更新数据库，不影响主流程
                await asyncio.to_thread(traverse_img.update_file_id, media_id, new_file_id)
                
    except Exception as e:
        logging.error(f"发送图片失败: {e}")
        await bot.send_message(chat_id=chat_id, text="发送图片失败，可能是某张图片已损坏或不存在。")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户发送的普通文本消息（包含快捷按钮的“抽！”和网址）"""
    url = update.message.text
    chat_id = update.effective_chat.id
    
    # 分支 1：处理抽图指令
    if url == "抽！":
        await chou_logic(chat_id, context.bot)
        return # 抽完图直接结束，不要往下走

    # 分支 2：处理爬取链接（需管理员权限）
    # 在业务逻辑里拦截非管理员
    if chat_id not in ADMIN_IDS:
        logging.info(f"{chat_id} - unauthed_one - {url}")
        await update.message.reply_text('爬取功能暂不对外开放')
        return  # 【安全修复】：必须 return，防止越权执行后续爬虫代码
        
    logging.info(f"{chat_id} 请求解析 URL: {url}")
    
    try:
        # 兼容手机版链接
        if 'mob' in url:
            url = url.replace('mob', 'data')
            
        # 假设 get_url 是基于 requests 的同步网络请求，必须用 to_thread 防止阻塞机器人
        result_msg = await asyncio.to_thread(get_url.get_1024_url, str(url))
        await update.message.reply_text(str(result_msg))
    except Exception as e:
        logging.error(f"解析链接出错: {e}")
        await update.message.reply_text('Bad link or process error')


async def show_at_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /show 命令（抽图）"""
    await chou_logic(update.effective_chat.id, context.bot)


async def list_img_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    处理 /list 命令。
    触发增量扫描本地图库并同步到数据库。
    """
    # 提示用户正在同步（因为如果图多，扫描磁盘可能会耗时几秒钟）
    processing_msg = await update.message.reply_text("正在扫描磁盘增量同步图库，请稍候...")
    
    try:
        # 遍历磁盘属于极高耗时的阻塞操作，必须放进线程池执行
        res = await asyncio.to_thread(traverse_img.reset_media_db)
        # 同步完成后修改提示消息
        await processing_msg.edit_text(str(res))
    except Exception as e:
        logging.error(f"数据库重置失败: {e}")
        await processing_msg.edit_text(f'发生错误: {e}')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """处理取消对话状态"""
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


if __name__ == '__main__':
    # 构建机器人应用
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # 1. 注册普通文本处理器 (拦截非命令的纯文本，如 "抽！" 或 网址)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    # 2. 注册管理员专用的命令 /list 
    # 【安全修复】：利用 filters=admin_filter 在路由层直接拦截非管理员，更优雅安全
    list_img_handler = CommandHandler('list', list_img_db, filters=admin_filter)
    
    # 3. 注册带状态的会话处理器（适用于包含 /start 初始化及后续状态机的交互）
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOU: [CommandHandler("show", show_at_random)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 4. 注册 /show 命令 (允许用户不经过 /start 直接通过命令调用抽图)
    send_1024_pic = CommandHandler('show', show_at_random)

    # 将所有 Handler 挂载到 application
    application.add_handler(conv_handler)
    application.add_handler(echo_handler)
    application.add_handler(send_1024_pic)
    application.add_handler(list_img_handler)

    # 启动轮询
    logging.info("Bot is running...")
    application.run_polling()