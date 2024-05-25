import numpy as np
import matplotlib.pyplot as plt
from Control_TwoSticksClasssicPydroidVideo import inverted_power_response_signed

# Define the power parameter
POWER_PARAMETER = 0.4

# Generate values of A_stick from -1 to 1
A_stick_values = np.linspace(-1, 1, 400)
response_values = [inverted_power_response_signed(A, power=POWER_PARAMETER) for A in A_stick_values]

# Plotting the response curve
plt.figure(figsize=(10, 6))
plt.plot(A_stick_values, response_values, label=f'Power={POWER_PARAMETER}')
plt.title('Inverted Power Response Signed')
plt.xlabel('A_stick')
plt.ylabel('Response')
plt.legend()
plt.grid(True)
plt.show()
