import uasyncio as asyncio
import network
import urequests
import json
import time
from machine import Pin

# Конфигурация
import config
SSID = config.SSID
PASSWORD = config.PASSWORD

CITY = "Moscow"
USE_FREE_API = True  # True для wttr.in

# Светодиод для индикации
led = Pin(2, Pin.OUT)

# Состояние подключения
wifi_connected = False
wlan = None

async def connect_wifi():
    """Асинхронное подключение к Wi-Fi"""
    global wifi_connected, wlan
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        wifi_connected = True
        print("Уже подключено к Wi-Fi")
        print("IP адрес:", wlan.ifconfig()[0])
        return True
    
    print("Подключение к Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Асинхронное ожидание подключения
    timeout = 30  # таймаут 30 секунд
    while timeout > 0:
        if wlan.isconnected():
            wifi_connected = True
            print("\nПодключено!")
            print("IP адрес:", wlan.ifconfig()[0])
            led.value(1)
            return True
        
        # Мигаем светодиодом
        led.toggle()
        print(".", end="")
        
        await asyncio.sleep(0.5)
        timeout -= 0.5
    
    print("\nОшибка подключения к Wi-Fi")
    led.value(0)
    return False

async def check_wifi_connection():
    """Проверка и восстановление Wi-Fi соединения"""
    global wifi_connected
    
    while True:
        if wlan and not wlan.isconnected():
            print("Потеряно соединение с Wi-Fi. Переподключение...")
            wifi_connected = False
            led.value(0)
            
            # Пытаемся переподключиться
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            
            timeout = 20
            while timeout > 0 and not wlan.isconnected():
                await asyncio.sleep(0.5)
                timeout -= 0.5
            
            if wlan.isconnected():
                wifi_connected = True
                led.value(1)
                print("Wi-Fi восстановлен!")
            else:
                print("Не удалось восстановить Wi-Fi")
        
        await asyncio.sleep(5)  # Проверяем каждые 5 секунд

async def get_weather_free():
    """Асинхронное получение погоды через wttr.in"""
    try:
        url = f"https://wttr.in/{CITY}?format=%t+%c+%w+%h&m"
        print(f"Запрос погоды для {CITY}...")
        
        # Используем urequests в асинхронном режиме
        await asyncio.sleep(0)
        response = urequests.get(url)
        
        if response.status_code == 200:
            weather_data = response.text.strip()
            response.close()
            return weather_data
        else:
            print(f"Ошибка HTTP: {response.status_code}")
            response.close()
            return None
            
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None

async def weather_updater():
    """Асинхронное обновление погоды"""
    while True:
        if wifi_connected:
            weather = await get_weather_free()
            
            if weather:
                print(f"\n=== Погода в {CITY} ===")
                print(f"Данные: {weather}")
                
                # Сигнал успешного получения
                for _ in range(2):
                    led.value(0)
                    await asyncio.sleep(0.2)
                    led.value(1)
                    await asyncio.sleep(0.2)
            else:
                print("Не удалось получить погоду")
                # Сигнал ошибки
                for _ in range(3):
                    led.toggle()
                    await asyncio.sleep(0.1)
        else:
            print("Ожидание подключения к Wi-Fi...")
        
        # Ждем 60 секунд перед следующим обновлением
        await asyncio.sleep(60)

async def blink_led():
    """Асинхронное мигание светодиодом (для демонстрации параллельной задачи)"""
    while True:
        if not wifi_connected:
            # Медленное мигание при отсутствии Wi-Fi
            led.value(0)
            await asyncio.sleep(0.5)
            led.value(1)
            await asyncio.sleep(0.5)
        else:
            # Редкое мигание при нормальной работе
            await asyncio.sleep(5)
            led.value(0)
            await asyncio.sleep(0.1)
            led.value(1)

async def button_handler():
    """Асинхронная обработка кнопки (пример с кнопкой на GPIO0)"""
    button = Pin(0, Pin.IN, Pin.PULL_UP)
    
    while True:
        if button.value() == 0:  # Кнопка нажата
            print("Кнопка нажата! Обновляем погоду...")
            weather = await get_weather_free()
            if weather:
                print(f"Погода: {weather}")
            
            # Защита от дребезга
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(0.1)

async def main():
    """Главная асинхронная функция"""
    print("Запуск асинхронной программы...")
    
    # Подключаемся к Wi-Fi
    await connect_wifi()
    
    # Создаем и запускаем асинхронные задачи
    tasks = [
        asyncio.create_task(check_wifi_connection()),
        asyncio.create_task(weather_updater()),
        asyncio.create_task(blink_led()),
        # asyncio.create_task(button_handler()),  # Раскомментируйте для использования кнопки
    ]
    
    # Запускаем все задачи
    await asyncio.gather(*tasks)

# Запуск программы
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nПрограмма остановлена")
except Exception as e:
    print(f"Ошибка: {e}")