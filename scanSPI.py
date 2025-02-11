import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
print("I2C Scan...")
while not i2c.try_lock():
    pass
try:
    devices = i2c.scan()
    print("I2C devices found:", [hex(d) for d in devices])
finally:
    i2c.unlock()
