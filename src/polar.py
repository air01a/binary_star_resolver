import cv2
import numpy as np
import matplotlib.pyplot as plt

def autocorrelation(image):
    # Convertir l'image en niveaux de gris
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculer la FFT de l'image
    f = np.fft.fft2(gray_image)
    fshift = np.fft.fftshift(f)
    
    # Calculer le spectre de magnitude et effectuer une autocorrélation
    magnitude_spectrum = 20 * np.log(np.abs(fshift))
    autocorr = np.fft.ifftshift(np.fft.ifft2(np.abs(fshift)**2))
    
    return np.abs(autocorr)

def to_polar_coordinates(image):
    # Obtenir les dimensions de l'image
    height, width = image.shape[:2]
    max_radius = np.sqrt((height/2)**2 + (width/2)**2)
    
    # Créer une grille en coordonnées polaires
    r = np.linspace(0, max_radius, max(height, width))
    theta = np.linspace(0, 2*np.pi, 360)
    R, Theta = np.meshgrid(r, theta)
    
    # Conversion en coordonnées cartésiennes
    X = R * np.cos(Theta) + width // 2
    Y = R * np.sin(Theta) + height // 2
    
    # Interpolation pour obtenir les valeurs en coordonnées polaires
    polar_image = cv2.remap(image, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_LINEAR)
    
    return polar_image

# Charger l'image
image_path = '../../test.png'
image = cv2.imread(image_path)

# Calculer l'autocorrélation
autocorr_image = autocorrelation(image)
plt.imshow(autocorr_image, cmap='gray')
plt.title('Autocorrélation en coordonnées polaires')
plt.show()
# Convertir l'autocorrélation en coordonnées polaires
polar_autocorr = to_polar_coordinates(autocorr_image)

# Afficher l'autocorrélation en coordonnées polaires
plt.imshow(polar_autocorr, cmap='gray')
plt.title('Autocorrélation en coordonnées polaires')
plt.show()