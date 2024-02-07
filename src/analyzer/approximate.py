import numpy as np
from scipy.optimize import minimize, least_squares
import matplotlib.pyplot as plt


# Définir la fonction F(x, y)
def F(x, params):
    #x0_1, y0_1, A1, x0_2, y0_2, A2, a, b, B = params
    A1, d1,  C, a, b,a2,b2 = params
    return 1 * np.exp(-b*x**2)/(1+a*x**2) + A1*(np.exp(-b2 * (x-d1)**2)/(1+a2*(x-d1)**2) + np.exp(-b2 * (x+d1)**2)/(1+a2*(x+d1)**2))+C

def residuals(params, x_data, y_data):
    predicted_z = F(x_data, params)
    return predicted_z - y_data

def approximate(x_init,y_init,A1_init=0.25, d1_init=0.01):
    print("******************************")
    print("Approximation ")
    print(f"A1_init : {A1_init}, d1_init : {d1_init}")
    x_init = np.array(x_init)
    y_init = np.array(y_init)
    y = (y_init -y_init.min())/(y_init.max() - y_init.min())
    x=x_init/x_init.max()
    initial_parameters=[A1_init,-d1_init,y[0],200,200,200,200]
    bounds = [(A1_init*0.9, A1_init*1.1), (-0.9, -0.01), (0,1), (1, 1000), (1, 1000),(1, 1000), (1, 1000)]

    result2 = minimize(cost_function, initial_parameters, args=(x, y),bounds=bounds)
    print(result2.x)
    A1, d1, C, a, b,a2,b2 = result2.x 
    print(0.099*x_init.max()*(-d1))
    print("******************************")
    return result2

def simulation(x,params):
    x = np.array(x)
    x = x/x.max()
    return F(x, params)

def cost_function(params, x_data, y_data):
    total_error = 0
    for x, y in zip(x_data, y_data):
        total_error += (F(x, params) - y)**2
    return total_error



if __name__=='__main__':
    x=np.array([-43.0, -42.0, -41.0, -40.0, -39.0, -38.0, -37.0, -36.0, -35.0, -34.0, -33.0, -32.0, -31.0, -30.0, -29.0, -28.0, -27.0, -26.0, -25.0, -24.0, -23.0, -22.0, -21.0, -20.0, -19.0, -18.0, -17.0, -16.0, -15.0, -14.0, -13.0, -12.0, -11.0, -10.0, -9.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0])
    y=np.array([560.1647, 572.4964, 663.019, 671.48694, 662.7555, 662.7555, 687.123, 685.702, 729.94183, 798.94336, 848.1526, 909.3145, 887.69995, 723.6184, 620.0811, 555.27454, 609.7626, 752.1902, 724.45355, 674.22864, 666.145, 587.5078, 510.92194, 510.44855, 510.44855, 560.96454, 660.7333, 937.9411, 1303.1285, 1596.6755, 2047.3364, 3120.9622, 4034.0225, 5195.979, 7662.621, 9514.028, 11029.236, 12135.797, 12217.97, 13385.047, 24853.293, 38188.996, 44665.45, 53338.39, 53338.39, 45128.41, 28152.305, 15768.868, 12228.057, 11471.325, 10085.692, 9533.695, 7765.8643, 6184.8364, 4490.919, 3483.7588, 2801.8877, 1915.9932, 1394.7671, 1011.8456, 768.7163, 683.45844, 640.3598, 495.34357, 495.34357, 523.2994, 597.6279, 645.6721, 636.04724, 636.6175, 628.834, 633.2664, 637.4639, 685.15424, 819.9862, 866.8572, 876.69275, 814.86084, 798.42395, 741.9525, 756.953, 752.6019, 712.29456, 712.29456, 690.5417, 633.2284, 594.8856, 589.3199])

    y = (y -y.min())/(y.max() - y.min())
    x_max = max(x)
    result2 = approximate(x,y)
    x=x/x_max

    Y2 = simulation(x, result2.x)
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='green')  # Utilisez 'marker' pour marquer les points de données
    #plt.plot(x, Y, marker='s', linestyle='--', color='red', label='y ls en fonction de x')
    plt.plot(x, Y2, marker='s', linestyle='--', color='blue', label='y minimize en fonction de x')


    plt.title('Graphique de y en fonction de x')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.show()