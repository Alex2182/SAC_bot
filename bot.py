# import PyPDF2
from tes import ocr
from planfact import pic_pf,effect,otk,devicewrk,find_artikul,artikul_history
#import telegram_send
import subprocess
# import telegram
#from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, callbackcontext
users_list=['add','users','ID','for','allow','access']
shop_list=['211', '216', '231', '236', '241', '251', '256', '290', '295', '360']
devicewrk_list=['211', '241', '360']

def hello(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        update.message.reply_text(f'Привет {update.effective_user.first_name}. Используй команды для получения информации.')
    else:
        update.message.reply_text(f'Привет {update.effective_user.first_name}. Вас нет в списке разрешенных пользователей. Свяжитесь с администратором бота.')

def start(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        #if context.args:
        #    text_caps = context.args[0]
        #    context.bot.send_message(chat_id=update.effective_chat.id,text=text_caps)
        #else:
            #if update.effective_user.id in users_list:
         context.bot.send_message(chat_id=update.effective_chat.id, text=f'Добро пожаловать {update.effective_user.first_name}!')
    else:
         context.bot.send_message(chat_id=update.effective_chat.id, text='Вас нет в списке разрешенных пользователей')

def pdf(update,context):
    try:
        newFile = update.message.effective_attachment.get_file()
        FileName = newFile.file_id
        #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Saved {FileName}')
        subprocess.run(['rm', '1.pdf'])
        newFile.download(custom_path='1.pdf')
        subprocess.run(['pdftotext', '1.pdf', '1.txt'])
        context.bot.send_document(chat_id=update.effective_chat.id, document=open('1.txt', 'rb'))
        #with open('1.txt', 'r') as txt_file:
            #pdf_reader = txt_file.read()
            # printing first page contents
            #pdf_page = pdf_reader.getPage(0)
            #text=pdf_page.extractText()
            #context.bot.send_message(chat_id=update.effective_chat.id, text=pdf_reader)
    except Exception as err:
       update.message.reply_text(f'Ошибка PDF {err}')

def tesseract(update,context):
    try:
        newFile = update.message.photo[-1].get_file()
        FileName = newFile.file_id
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Saved {FileName}')
        newFile.download()
    except Exception as err:
       update.message.reply_text(f'Error {err}')

def image(update,context):
    try:
    # file_info = context.bot.get_file(update.message.photo[len(update.message.photo) - 1].file_id)
        file = context.bot.get_file(update.message.photo[-1].file_id)
        file.download(custom_path='1.jpg')
    # downloaded_file = context.bot.download(file_info.file_path)
    # src =  update.message.photo[1].file_id
    # with open(src, 'wb') as new_file:
    #    new_file.write(downloaded_file)
        text = ocr('1.jpg')
        update.message.reply_text(text)
    except Exception as err:
        update.message.reply_text(f'Ошибка IMAGE {err}')

def planfact(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        try:
            pic_pf()
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('lastplanfact.png', 'rb'))
        except Exception as err:
            update.message.reply_text(f'Ошибка IMAGE {err}')

def effectivity(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        try:
            if context.args:
                shop = context.args[0]
                if shop in shop_list:
                    effect(shop)
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('effect.png', 'rb'))
                else:
                    update.message.reply_text(f'Ошибка. Цех {shop} не найден в списке.')
                    effect('Итого')
            else:
                update.message.reply_text('Цех не задан. Можете задать цех так: /effect <номер цеха>')
                effect('Итого')
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('effect.png', 'rb'))
        except Exception as err:
            update.message.reply_text(f'Ошибка IMAGE {err}')

def pic_otk(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        try:
            otk()
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('otk.png', 'rb'))
        except Exception as err:
            update.message.reply_text(f'Ошибка IMAGE {err}')

def pic_devwrk(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        if context.args:
            if context.args[0] in devicewrk_list:
                try:
                    devicewrk(context.args[0])
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('devicewrk.png', 'rb'))
                except Exception as err:
                    update.message.reply_text(f'Ошибка IMAGE {err}')
            else:
                update.message.reply_text(f'Доступна статистика только по цехам {devicewrk_list}')
        else:
            update.message.reply_text(f'Использование команды /dev_work <номер цеха> из списка 211, 241, 360')

def get_tvz_artikul(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        if context.args:
            # if context.args[0] in devicewrk_list:
            try:
                find_artikul(context.args[0])
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('tvz.png', 'rb'))
            except Exception as err:
                update.message.reply_text(f'Ошибка IMAGE {err}')
        else:
            update.message.reply_text(f'Использование команды /a артикул')

def get_artikul_history(update,context):
    if (allow(update.effective_user.id,update.effective_user.first_name,update.effective_user.last_name)):
        if context.args:
            # if context.args[0] in devicewrk_list:
            try:
                text = artikul_history(context.args[0])
                #context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('tvz.png', 'rb'))
                #update.message.reply_text(text=text)
#                telegram_send.send(messages=[text])
            except Exception as err:
                update.message.reply_text(f'Ошибка Artikul_history {err}')
        else:
            update.message.reply_text(f'Использование команды /ah артикул')


def allow(user_id,first_name,last_name):
    if user_id in users_list:
        return True
    else:
       # Alert for strange users
#       telegram_send.send(messages=['Stranger alert',f'{user_id} {first_name} {last_name}'])
       return False

updater = Updater('tg_ID')

updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), hello))
# PDF catch
updater.dispatcher.add_handler(MessageHandler(Filters.document.pdf, pdf))
#Image catch
updater.dispatcher.add_handler(MessageHandler(Filters.photo, image))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('planfact', planfact))
updater.dispatcher.add_handler(CommandHandler('effect', effectivity))
updater.dispatcher.add_handler(CommandHandler('otk', pic_otk))
updater.dispatcher.add_handler(CommandHandler('dev_work', pic_devwrk))
updater.dispatcher.add_handler(CommandHandler('a', get_tvz_artikul))
updater.dispatcher.add_handler(CommandHandler('ah', get_artikul_history))



updater.start_polling()
updater.idle()

