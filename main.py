from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import io
import telebot

# Встановлюємо кодування для виведення на консоль
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Telegram bot setup
bot_token = "7835773967:AAF_wU4W3QVmKnqAOtxvpnPFM2RmODzkE4c"
user_id = 718260754
bot = telebot.TeleBot(bot_token)

def send_telegram_message(data):
    message = (
        "🎉 <b>Нові доступні слоти для запису! 🎉</b>\n\n"
        "<b>🗓️ Доступні дати та часи:</b>\n"
    )
    for entry in data:
        message += f"{entry}\n"
    message += (
        "\n💡 <i>Перевіряйте скоріше та бронюйте зручний час! </i>"
    )
    bot.send_message(user_id, message, parse_mode="HTML")

# Функція для читання даних із файлу
def read_data_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    return []

# Функція для запису даних у файл
def write_data_to_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in data:
            file.write(entry + "\n")

# Ініціалізація браузера
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# URL для входу
url = "https://app.mindlyspace.com/auth"
driver.get(url)

try:
    # Вибір мови
    ukrainian_language_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Українська')]")
    ))
    ukrainian_language_option.click()

    # Авторизація (Login example)
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Продовжити з Email']")
    ))
    login_button.click()

    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    email_input.send_keys("romanov.andrus.michael@gmail.com")

    next_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Далі']")
    ))
    next_button.click()

    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
    password_input.send_keys("P@ssword")

    login_submit = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Увійти')]")
    ))
    login_submit.click()

    # Натискаємо на кнопку "Записатися на сеанс"
    book_session_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Записатися на сеанс')]")
    ))
    book_session_button.click()

    # Очікування завантаження сторінки
    time.sleep(5)

    # Отримання доступних дат
    days_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//ion-slide/button/span")
        )
    )

    available_dates = [el.text.strip() for el in days_elements]

    # Отримання доступних часових слотів для кожної дати
    available_slots = []
    for date_element in days_elements[:7]:  # Обмеження до 7 днів
        date_element.click()  # Клік по даті, щоб завантажити часи
        time.sleep(1)
        slots_elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "booking")
            )
        )
        slots = [slot.text.strip() for slot in slots_elements]
        available_slots.append({date_element.text.strip(): slots})

    # Формуємо дані для запису у файл
    combined_data = []
    for date, slots in zip(available_dates[:7], available_slots):  # Перші 7 днів
        slots_str = ", ".join(slots[date]) if date in slots else "No slots"
        combined_data.append(f"{date}: {slots_str}")

    # Шлях до файлу для зберігання даних
    file_path = "text.txt"

    # Читання попередніх даних і порівняння
    previous_data = read_data_from_file(file_path)

    if combined_data != previous_data:
        write_data_to_file(file_path, combined_data)
        send_telegram_message(combined_data)

finally:
    # Закриваємо браузер
    driver.quit()
