import math
import numpy as np
import cv2
from image_utils.image_manager import ImageManager,SerManager
from os import listdir
from os.path import splitext, isfile, isdir
from image_utils.processing import AstroImageProcessing
from findpeaks import findpeaks


def calculate_line(point_a, point_b, variance=0.0):
     
    (x1,y1) = point_a
    (x2,y2) = point_b


    m = (y2-y1)/(x2-x1)*(1+variance*5)
    p = y1-m*x1
    return(m,p)


def calculate_perp(m, point):
    (x,y) = point
    m_perp = -1 / m
    p = y -m_perp * x
    return (m_perp,p)

def detect_and_remove_lines(image):

    (h,w) = image.shape
    for i in range(int(w/2-0.3*w),int(w/2+0.3*w)):
        image[int(h/2), i] = (image[int(h/2)-1, i] + image[int(h/2)+1, i])/2
        image[i, int(h/2)] = (image[i,int(h/2)-1] + image[i,int(h/2)+1])/2
    return image



def circle_calculation(pts):
    x1, y1 = pts[0,0]
    x2, y2 = pts[1,0]
    x3, y3 = pts[2,0]

    # Calcul des médiatrices pour les segments [P1P2] et [P1P3]
    ma = (y2 - y1) / (x2 - x1)
    mb = (y3 - y1) / (x3 - x1)

    # Calcul du centre du cercle (xc, yc)
    xc = (ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x1 + x3)) / (2 * (mb - ma))
    yc = -1/ma * (xc - (x1 + x2) / 2) + (y1 + y2) / 2

    # Calcul du rayon
    rayon = np.sqrt((xc - x1)**2 + (yc - y1)**2)

    return (int(xc), int(yc)), int(rayon)


def angle_with_reference(centre, reference, point):
    vector1 = reference - centre
    vector2 = point - centre
    unit_vector_1 = vector1 / np.linalg.norm(vector1)
    unit_vector_2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)
    return angle

def erase_principal_disk(image, vector):

    # Exemple de profil d'intensité pour le disque central
    # Supposons que c'est un profil d'intensité linéaire pour simplifier l'exemple
    # Taille de l'image
    (image_size_x,image_size_y) = image.shape

    # Créer une matrice pour le disque central
    central_disk = np.zeros((image_size_x, image_size_y))

    # Calculer la distance de chaque point au centre de l'image
    centre_x = image_size_x / 2
    centre_y = image_size_y / 2
    for x in range(image_size_x):
        for y in range(image_size_y):
            distance = np.sqrt((x - centre_x)**2 + (y - centre_y)**2)
            distance_index = int(distance)

            # Utiliser le profil d'intensité pour définir la valeur du disque
            if distance_index < len(vector):
                central_disk[x, y] = vector[distance_index]
    #st.write(disque_central)
    #show_image(disque_central,"central disk",st)
    image = image - central_disk
    image[image<0]=0
    return (image, central_disk)




def get_vector_from_direction(image, m, point, max_range):
    
    x_C, y_C = point
    dx = 1 / math.sqrt(1 + m**2)  # Normalized
    dy = m * dx
    step=1
    vec = []
    for d in range(max_range):        
        x_C2_1 = int(x_C + d/step * dx)
        y_C2_1 = int(y_C + d/step * dy)
        x_C2_2 = int(x_C - d/step * dx)
        y_C2_2 = int(y_C - d/step * dy)
        if x_C2_1<image.shape[0] and y_C2_1<image.shape[1] and x_C2_2<image.shape[0] and y_C2_2<image.shape[1]:
            vec.append((image[y_C2_1,x_C2_1]+image[y_C2_2,x_C2_2])/2)

    return vec


def slice_from_direction(image, m, point):
    image = image.copy()

    d_max = math.sqrt(image.shape[0]**2 + image.shape[1]**2) / 2

    dx = 1 / math.sqrt(1 + m**2)  # Normalized
    dy = m * dx

    curve = []
    step = 1

    x_C,y_C = point
    for d in range(0, int(d_max)*step):
        # Calculate 2 points
        # with parametric formulation of a line
        x_C2_1 = x_C + d/step * dx
        y_C2_1 = y_C + d/step * dy

        x_C2_2 = x_C - d/step * dx
        y_C2_2 = y_C - d/step * dy

        if 0 <= x_C2_1 < image.shape[0] and 0 <= y_C2_1 < image.shape[1]:
            curve.append([d/step,image[int(y_C2_1),int(x_C2_1)]])

        
        if 0 <= x_C2_2 < image.shape[0] and 0 <= y_C2_2 < image.shape[1]:
            curve.append([-d/step,image[int(y_C2_2),int(x_C2_2)]])
    

    curve = sorted(curve, key=lambda pair: pair[0])
    return curve

def find_contours(src):
    image=(src.copy()/src.max() * 255).astype(np.uint8)
    image = cv2.bilateralFilter(image, 15, 75, 75) 
    ret, thresh = cv2.threshold(image, 0.8, 255, 0)
    contours, hierarchy = cv2.findContours((thresh).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours=sorted(contours, key=cv2.contourArea, reverse=True)
    return contours


def find_ellipse(contour):
    ellipse = cv2.fitEllipse(contour)
    centre, axes, angle = ellipse
    axe1, axe2 = axes[0] / 2, axes[1] / 2
    major_axe = max(axe1,axe2)
    minor_axe = min(axe1,axe2)
    c = np.sqrt(major_axe**2 - minor_axe**2)
    angle_rad = np.deg2rad(angle-90)
    focus1 = (int(centre[0] + c * np.cos(angle_rad)), int(centre[1] + c * np.sin(angle_rad)))
    focus2 = (int(centre[0] - c * np.cos(angle_rad)), int(centre[1] - c * np.sin(angle_rad)))


    return (ellipse, major_axe, minor_axe, angle_rad, focus1, focus2)

def find_peaks(curve):
    
    #y = y-smoothed_y_values


    grads = []
    x2=[]
    peaks=[]
    in_peak=False
    first_peak=-1
    for i in range(1,len(curve)-1):
        x2.append(i)
        grad = 0.0 + (curve[i+1][1]-curve[i][1])
        if grad>0:
            in_peak=True
            first_peak=-1
            
        if grad<0:
            if in_peak:
                if first_peak!=-1:

                    ind = i-(i - first_peak)//2
                else:
                    ind=i

                    
                peaks.append([ind,curve[ind][1]])
            first_peak = -1
            in_peak=False


        if grad==0 and in_peak and first_peak==-1:
            first_peak = i

        last = grad
        grads.append(grad)

    peaks = sorted(peaks, key=lambda pair: pair[1], reverse=True)
    return peaks,grads



def load_speckle_images(image_files):
    imager = ImageManager()
    if isinstance(image_files, list):
        tab =  [roi for roi in [AstroImageProcessing.find_roi(imager.read_image(file)) for file in image_files] if roi is not None]
    elif isinstance(image_files, str):
        ser = SerManager(image_files)
        tab = [roi for roi in [AstroImageProcessing.find_roi(np.squeeze(ser.get_img(index))) for index in range(ser.header.frameCount)] if roi is not None]
    else:
        return None

    max_w = 0
    max_h = 0
    for im in tab:
        (h, w) = im.shape
        max_w = max(w, max_w)
        max_h = max(h, max_h)
    max_size = max(max_w, max_h)
    if max_size % 2!=0:
        max_size+=1
    output = []
    for index, im in enumerate(tab):
        if tab[index] is not None and len(tab[index]>0):
            output.append(AstroImageProcessing.resize_with_padding(im, max_size, max_size))

    output = order_by_peak(output)
    return output

def get_image_from_directory(dir):
    image_files=[]
    for file in listdir(dir):
        file_path = dir + '/' + file
        if isfile(file_path) and splitext(file_path)[1]=='.fit':
            image_files.append(file_path)

    
    return image_files


def find_brightest_pixel(image):
    """ Trouve la position du pixel le plus lumineux dans l'image. """
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    return max_loc

def align_images_correlation(image1, image2):
    # Convertir les images en niveaux de gris
    gray1 = ((image1-image1.min())/(image1.max() - image1.min())*255).astype(np.uint8)
    gray2 = ((image2-image2.min())/(image2.max() - image2.min())*255).astype(np.uint8)

    # Calculer l'intercorrélation entre les deux images
    correlation_output = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
    
    # Trouver la position du maximum de corrélation
    _, _, _, max_loc = cv2.minMaxLoc(correlation_output)
    return max_loc
    # Calculer le décalage entre les images
    #x_offset = max_loc[0]
    #y_offset = max_loc[1]

    # Aligner la deuxième image sur la première
    #aligned_image = cv2.warpAffine(image2, np.float32([[1, 0, x_offset], [0, 1, y_offset]]), (image1.shape[1], image1.shape[0]))


def align_images(images):
    """ Aligner les images en s'assurant qu'elles ont toutes la même taille finale. """
    #brightest_pixels = [find_brightest_pixel(img) for img in images]
    ref = images[0]
    brightest_pixels  = [align_images_correlation(ref,img) for img in images]
    # Trouver les décalages maximaux pour aligner les images
    max_x = max([p[0] for p in brightest_pixels])
    max_y = max([p[1] for p in brightest_pixels])

    # Calculer les dimensions finales nécessaires
    max_width = max([img.shape[1] + (max_x - x) for img, (x, y) in zip(images, brightest_pixels)])
    max_height = max([img.shape[0] + (max_y - y) for img, (x, y) in zip(images, brightest_pixels)])


    aligned_images = [ref]
    for img, (x, y) in zip(images, brightest_pixels):
        dx, dy = max_x - x, max_y - y

        # Créer une nouvelle image avec les dimensions finales
        new_image = np.zeros((max_height, max_width), dtype=img.dtype)
        new_image[dy:dy+img.shape[0], dx:dx+img.shape[1]] = img
        aligned_images.append(new_image)

    return aligned_images

def sum_aligned_images(images):
    """ Somme des images alignées. """
    aligned_images = align_images(images)
    sum_image = np.zeros_like(aligned_images[0]).astype(np.float32)
    i=0
    for img in aligned_images:
        # Évite la saturation
        sum_image=sum_image+img
        i+=1

    return sum_image/i

def detect_peaks(image):
    gray = (255*(image - image.min())/(image.max()-image.min())).astype(np.uint8)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    fp = findpeaks(method='mask',denoise="mean")

    res=(fp.fit(blurred)['Xdetect']*image)
    (x,y) = find_brightest_pixel(res)
    res[y,x]=0
    (x2,y2) = find_brightest_pixel(res)

    #cv2.circle(image,(x2,y2),2,image.max()*1.1,-1)
    #cv2.circle(image,(x,y),2,image.max()*1.1,-1)
    #-show_image(image)
    return (x,y, x2,y2)



def isolate_peaks(image, radius=1):
    gray = (255*(image - image.min())/(image.max()-image.min())).astype(np.uint8)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    fp = findpeaks(method='mask',denoise="mean")

    res=(fp.fit(gray)['Xdetect']*blurred)
    (x,y) = find_brightest_pixel(res)
    cv2.circle(res, (x,y),radius,0,-1)
    (x2,y2) = find_brightest_pixel(res)

    return (x,y, x2,y2)


def order_by_peak(images):
    best_frames = []

    for index, im in enumerate(images):
        best_frames.append([im.max(), im])
    sorted_result = sorted(best_frames, key=lambda x: x[0], reverse=True)
    result = [r[1] for r in sorted_result]
    return result

def angle_with_y_axis(x1, y1, x2, y2):
    # Calcul de l'angle en radians par rapport à l'axe des X
    angle_rad = math.atan2(y2 - y1, x2 - x1)

    # Conversion en angle par rapport à l'axe des Y
    angle_y_rad = math.pi / 2 - angle_rad

    # Conversion de radians en degrés
    angle_deg = math.degrees(angle_y_rad)

    return angle_deg



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