import lgpio

h = lgpio.gpiochip_open(0)
TRIAC_PIN = 23 
lgpio.gpio_claim_output(h, TRIAC_PIN)
#lgpio.gpio_write(h, TRIAC_PIN, 0)

stan = lgpio.gpio_read(h, TRIAC_PIN)

print(f"Stan pinu {TRIAC_PIN}: {stan}")
