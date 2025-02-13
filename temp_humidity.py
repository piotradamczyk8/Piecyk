import board
import busio
import adafruit_sht31d

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)
print(sensor)

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
