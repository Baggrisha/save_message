import datetime

from aiogram import Router, F, Bot
from aiogram.types import *

from configs.settings import TOKEN, admin

router_main = Router()
bot = Bot(token=TOKEN)
business_messages_cache = {}


@router_main.business_message(F.from_user.id != admin)
async def handle_business_message(conn=BusinessConnection):
    cache = business_messages_cache.setdefault(conn.chat.id, {})
    cache[conn.message_id] = {
        "text": conn.text or None,
        "photo": conn.photo[-1].file_id if conn.photo else None,
        "video": conn.video.file_id if conn.video else None,
        "voice": conn.voice.file_id if conn.voice else None,
        "video_note": conn.video_note.file_id if conn.video_note else None,
        "document": conn.document.file_id if conn.document else None,
        "sticker": conn.sticker.file_id if conn.sticker else None,
        "animation": conn.animation.file_id if conn.animation else None,
        "caption": getattr(conn, "caption", None),
        "media_group_id": getattr(conn, "media_group_id", None)
    }


@router_main.business_connection()
async def business_connected(conn=BusinessConnection):
    if conn.is_enabled:
        await bot.send_message(
            chat_id=conn.user_chat_id,
            text=f"Аккаунт подключен"
        )
    else:
        await bot.send_message(
            chat_id=conn.user_chat_id,
            text=f"Аккаунт отключен")


@router_main.deleted_business_messages()
async def deleted_message(conn=BusinessConnection):
    chat_id = conn.chat.id
    text_header = (f'<a href="https://t.me/{conn.chat.username}">{conn.chat.full_name}</a>, '
            f'{conn.chat.id} удалил(а) сообщение')

    media_groups: dict[str, list] = {}
    single_msgs = []

    for message_id in conn.message_ids:
        try:
            msg = business_messages_cache[chat_id][message_id]
            group_id = msg.get("media_group_id")
            if group_id:
                media_groups.setdefault(group_id, []).append(msg)
            else:
                single_msgs.append(msg)
        except KeyError:
            single_msgs.append(None)

    # Одиночные сообщения
    for msg in single_msgs:
        if msg is None:
            await bot.send_message(chat_id=admin,
                                   text=f'{text_header}\n\n<blockquote> [содержание недоступно]</blockquote>',
                                   parse_mode='HTML', disable_web_page_preview=True)

            break

        if msg["text"]:
            await bot.send_message(chat_id=admin,
                                   text=f'{text_header}\n\n<blockquote> {msg["text"]}</blockquote>',
                                   parse_mode='HTML',
                                   disable_web_page_preview=True)
        else:
            await bot.send_message(chat_id=admin, text=text_header, parse_mode='HTML', disable_web_page_preview=True)


        if msg["photo"]:
            await bot.send_photo(chat_id=admin, photo=msg["photo"], caption=msg["caption"])
        if msg["video"]:
            await bot.send_video(chat_id=admin, video=msg["video"], caption=msg["caption"])
        if msg["voice"]:
            await bot.send_voice(chat_id=admin, voice=msg["voice"], caption=msg["caption"])
        if msg["video_note"]:
            await bot.send_video_note(chat_id=admin, video_note=msg["video_note"])
        if msg["document"]:
            await bot.send_document(chat_id=admin, document=msg["document"], caption=msg["caption"])
        if msg["sticker"]:
            await bot.send_sticker(chat_id=admin, sticker=msg["sticker"])
        if msg["animation"]:
            await bot.send_animation(chat_id=admin, animation=msg["animation"], caption=msg["caption"])

    # Медиа-группы
    for group_msgs in media_groups.values():
        media_list = []
        caption_used = False
        for msg in group_msgs:
            if msg["photo"]:
                media_list.append(InputMediaPhoto(media=msg["photo"],
                                                  caption=msg["caption"] if not caption_used else None))
                caption_used = True
            elif msg["video"]:
                media_list.append(InputMediaVideo(media=msg["video"],
                                                  caption=msg["caption"] if not caption_used else None))
                caption_used = True
            elif msg["document"]:
                media_list.append(InputMediaDocument(media=msg["document"],
                                                     caption=msg["caption"] if not caption_used else None))
                caption_used = True
            elif msg["animation"]:
                media_list.append(InputMediaAnimation(media=msg["animation"],
                                                      caption=msg["caption"] if not caption_used else None))
                caption_used = True

        if media_list:
            await bot.send_message(chat_id=admin, text=text_header, parse_mode='HTML', disable_web_page_preview=True)
            await bot.send_media_group(chat_id=admin, media=media_list)


@router_main.edited_business_message()
async def edited_message(conn=BusinessConnection):
    chat_id = conn.chat.id
    try:
        old_text = business_messages_cache[chat_id][conn.message_id]
    except KeyError:
        old_text = 'содержание недоступно'

    # Проверяем, изменился ли текст
    if not conn.text or conn.text == old_text:
        return  # если текста нет или он не поменялся — ничего не делаем
    text = (f'<a href="https://t.me/{conn.chat.username}">{conn.chat.full_name}</a>, '
            f'{conn.chat.id} изменил(а) сообщение')

    await bot.send_message(
        chat_id=admin,
        text=(f'{text}\n\n'
              f'<blockquote>старое:\n{old_text["text"]}\n</blockquote>\n\n'
              f'<blockquote>новое:\n{conn.text}</blockquote>'),
        parse_mode='HTML',
        disable_web_page_preview=True
    )


@router_main.error()
async def errors_h(error: ErrorEvent) -> None:
    with open('logs_main.log', 'a') as f:
        f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")} - [ERROR] {error.exception}\n')



