from machine import Pin, deepsleep

# configure input RTC pin with pull-up on boot
pin = Pin(2, Pin.IN, Pin.PULL_UP)

# disable pull-up and put the device to sleep for 10 seconds
pin.init(pull=None)
deepsleep(10000)
print('Сон завершен')