import board
import busio
import adafruit_sht31

# Inicjalizacja I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja sensora SHT31
sensor = adafruit_sht31.SHT31D(i2c)

# Odczyt temperatury i wilgotności
temperature = sensor.temperature
humidity = sensor.relative_humidity

print(f"Temperatura: {temperature:.2f} °C")
print(f"Wilgotność: {humidity:.2f} %")

# Opcjonalnie: sprawdzenie statusu grzałki
if sensor.heater:
    print("Grzałka jest włączona")
else:
    print("Grzałka jest wyłączona")

# Włączanie/wyłączanie grzałki
sensor.heater = True
