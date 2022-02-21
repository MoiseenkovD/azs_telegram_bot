import pandas as pd
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
import utils
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values('.env')

azs_df = pd.read_excel('azs.xlsx')

# Prepare regions ###############################

azs_df['Область'] = azs_df['Область'].str.strip()
regions = azs_df.drop_duplicates(subset=["Область"])['Область']

regions_buttons = []

for index, region in enumerate(regions):
    if isinstance(region, str) == False:
        break
    regions_buttons.append(InlineKeyboardButton(str(region), callback_data=f'set_region:{region}'))

# Prepare fuels ###############################

column_names = azs_df.keys()



# Handlers #######################################

def start(update: Update, context: CallbackContext):
    regions_keyboard = InlineKeyboardMarkup(utils.chunks(regions_buttons, 2))

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='В каком области вы живете?',
        reply_markup=regions_keyboard
    )


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    command, *payload = query.data.split(':')

    if command == 'set_region':

        fuels_button = []

        for index, column_name in enumerate(column_names):
            if index < 3 or index >= 9:
                continue
            fuels_button.append(InlineKeyboardButton(str(column_name), callback_data=f'set_fuel:{payload[0]}:{column_name}'))

        fuels_keyboard = InlineKeyboardMarkup(utils.chunks(fuels_button, 2))

        query.edit_message_text(text=f"📍Выбранная область: {payload[0]}")

        context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=f"Выберете ваше топливо:",
            reply_markup=fuels_keyboard
        )

    elif command == 'set_fuel':
        query.edit_message_text(text=f"⛽️Выбранное топливо: {payload[1]}")

        brand_price = []

        #fuel = azs_df[(azs_df['Область'] == payload[0]) &
        # (azs_df['Торговая марка'].notnull())][['Торговая марка', payload[1]]].dropna()

        #uel = azs_df[(azs_df['Область'] == payload[0]) &
        # (azs_df['Торговая марка'].notnull()) & (azs_df[payload[1]].dropna())][[‘Торговая марка', payload[1]]]

        # fuel = azs_df[(azs_df['Область'] == payload[0]) &
        #            (azs_df['Торговая марка'].notnull())][['Торговая марка', payload[1]]].dropna()

        fuel = azs_df[
            (azs_df['Область'] == payload[0]) &
            (azs_df['Торговая марка'].notnull()) &
            (azs_df[payload[1]].notnull())
        ][['Торговая марка', payload[1]]]

        for row in fuel.values:
            brand = row[0]
            price = row[1]
            brand_price.append(f'<strong>{brand}:</strong> {price} UAH \n')

        brand_price_str = ''.join(brand_price)

        context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=f'{brand_price_str}',
            parse_mode=ParseMode.HTML
        )


def main():
    bot = Bot(token=config['TG_TOKEN'])
    updater = Updater(bot=bot)

    start_handler = CommandHandler('start', start)
    updater.dispatcher.add_handler(start_handler)

    button_handler = CallbackQueryHandler(button)
    updater.dispatcher.add_handler(button_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


