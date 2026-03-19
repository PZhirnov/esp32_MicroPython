import network
import urequests
import json
import time
from machine import Pin
import ubinascii

# Конфигурация
import config
SSID = config.SSID
PASSWORD = config.PASSWORD

# API для погоды (пример с OpenWeatherMap)
API_KEY = "your_api_key_here"  # Зарегистрируйтесь на openweathermap.org для получения ключа
CITY = "Moscow"
# ИЛИ используйте бесплатное API без ключа (wttr.in)
USE_FREE_API = True  # True для wttr.in, False для OpenWeatherMap

# Светодиод для индикации (обычно встроенный на GPIO2)
led = Pin(2, Pin.OUT)

def save_in_file(data_txt):
    with open('history.txt', 'a', encoding='utf-8') as file:
        file.write('\n'+data_txt)


def connect_wifi():
    """Подключение к Wi-Fi сети"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Подключение к Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Мигаем светодиодом во время подключения
        timeout = 0
        while not wlan.isconnected() and timeout < 20:
            led.value(not led.value())
            time.sleep(0.5)
            timeout += 1
            print(".", end="")
        
        if wlan.isconnected():
            led.value(1)  # Включаем светодиод при успешном подключении
            print("\nПодключено!")
            config = wlan.ifconfig()
            print("IP адрес:", config[0])
            print("Маска подсети:", config[1])
            print("Шлюз:", config[2])
            print("DNS:", config[3])
            return True
        else:
            print("\nОшибка подключения к Wi-Fi")
            led.value(0)
            return False
    else:
        print("Уже подключено к Wi-Fi")
        config = wlan.ifconfig()
        print("IP адрес:", config[0])
        return True

def get_weather_free():
    """ПолучеÐ½ие погоды через бесплатное API wttr.in"""
    try:
        url = f"https://wttr.in/{CITY}?format=%t+%c+%w+%h&m"
        print(f"Запрос погоды для {CITY}...")
        
        response = urequests.get(url)
        
        if response.status_code == 200:
            weather_data = response.text.strip()
            save_in_file(weather_data)
            print(f"Погода получена: {weather_data}")
            response.close()
            return weather_data
        else:
            print(f"Ошибка HTTP: {response.status_code}")
            response.close()
            return None
            
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None

def get_weather_openweather():
    """Получение погоды через OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru"
        print(f"Запрос погоды для {CITY}...")
        
        response = urequests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            response.close()
            
            # Парсим данные
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            weather_desc = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            
            weather_info = {
                'temperature': temp,
                'feels_like': feels_like,
                'humidity': humidity,
                'pressure': pressure,
                'description': weather_desc,
                'wind_speed': wind_speed,
                'city': data['name']
            }
            
            return weather_info
        else:
            print(f"Ошибка HTTP: {response.status_code}")
            response.close()
            return None
            
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None

def display_weather(weather_data):
    """Отображение погоды в консоли"""
    if weather_data:
        if USE_FREE_API:
            print(f"\n=== Погода в {CITY} ===")
            print(f"Данные: {weather_data}")
        else:
            print(f"\n=== Погода в {weather_data['city']} ===")
            print(f"Температура: {weather_data['temperature']}Â°C")
            print(f"Ощущается как: {weather_data['feels_like']}Â°C")
            print(f"Описание: {weather_data['description']}")
            print(f"Влажность: {weather_data['humidity']}%")
            print(f"Давление: {weather_data['pressure']} гПа")
            print(f"Ветер: {weather_data['wind_speed']} м/с")
    else:
        print("Нет данных о погоде")

def main():
    """Основная функция"""
    print("Запуск программы...")
    
    # Подключаемся к Wi-Fi
    if not connect_wifi():
        print("Невозможно продолжить без подключения к Wi-Fi")
        return
    
    # Получаем погоду
    if USE_FREE_API:
        weather = get_weather_free()
    else:
        weather = get_weather_openweather()
    
    # Отображаем погоду
    display_weather(weather)
    
    # Мигаем светодиодом при успешном получении данных
    if weather:
        for _ in range(3):
            led.value(0)
            time.sleep(0.3)
            led.value(1)
            time.sleep(0.3)
    else:
        # Мигаем быстро при ошибке
        for _ in range(10):
            led.toggle()
            time.sleep(0.1)

# Запуск программы
if __name__ == "__main__":
    main()
    
    # Можно добавить цикл для периодического обновления
    while True:
        try:
            time.sleep(60)  # Ждем минуту
            print("\n--- Обновление погоды ---")
            if USE_FREE_API:
                weather = get_weather_free()
            else:
                weather = get_weather_openweather()
            display_weather(weather)
        except KeyboardInterrupt:
            print("\nПрограмма остановлена")
            break
        except Exception as e:
            print(f"Ошибка в цикле: {e}")