import time
import matplotlib.pyplot as plt
import lgpio

# Dane do wykresu
x_data = []
y_data = []
PIN = 23

# Funkcja do aktualizacji wykresu
def update_plot():
    plt.clf()
    plt.plot(x_data, y_data)
    plt.title("Mikrooscyloskop GPIO"+str(PIN))
    plt.xlabel("Czas (s)")
    plt.ylabel("Stan")
    plt.grid()
    plt.pause(0.000001)
    
h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_input(h, PIN)    

# Główna pętla
start_time = time.time()
while True:
    try:
        stan = lgpio.gpio_read(h, PIN)
        elapsed_time = time.time() - start_time
        x_data.append(elapsed_time)
        y_data.append(stan)

        if len(x_data) > 10:
            x_data.pop(0)
            y_data.pop(0)
            update_plot()
 
    except KeyboardInterrupt:
        lgpio.gpiochip_close(h)
        print("Zatrzymano!")
        break

plt.show()
