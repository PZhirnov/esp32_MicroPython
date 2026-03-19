# import time, machine

# led = machine.Pin(2, machine.Pin.OUT)

# while True:
#     led.value(1)
#     time.sleep(0.5)
#     led.value(0)
#     time.sleep(0.5)
#     print('Успешно')

import network
import urequests
import time
import machine

import config

# вывод индикатора
led = machine.Pin(2, machine.Pin.OUT)

# Настройки Wi-Fi
SSID = SSID
PASSWORD = PASSWORD



# Подключение к Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Подключаюсь к Wi-Fi", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(1)

print("\nПодключено! IP:", wlan.ifconfig()[0])

# Простой запрос погоды
while True:
    led.value(1)
    try:
        response = urequests.get("https://wttr.in/Moscow?format=%t+%c")
        if response.status_code == 200:
            print("Погода в Москве:", response.text.strip())
        response.close()
    except Exception as e:
        print("Ошибка:", e)
    led.value(0)
    for i in range(10):
        print(".", end="")
        
        time.sleep(1)
    print("\nПовторяю запрос")
