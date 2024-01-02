
from image_utils.image_utils import calculate_line, calculate_perp, detect_and_remove_lines, erase_principal_disk, \
                             find_contours,find_ellipse,get_vector_from_direction, find_peaks, slice_from_direction, detect_peaks
from image_utils.processing import AstroImageProcessing
from structure.message_queue import Message_Queue
import numpy as np
import cv2

class FrequencyAnalyzer:

    def __init__(self, broadcaster_out):
        self.min_value = 3000
        self.max_value = 40000
        self.mean_f = 3
        self.radius=2


    def psd(self, images):
        fouriers = []
        psd = []
        for im in images:
            fouriers.append(AstroImageProcessing.fourier_transform(im))
            psd.append(np.square(np.abs(AstroImageProcessing.fourier_transform(im))))
        
        psd_average= AstroImageProcessing.average_images((psd))
        spatial = AstroImageProcessing.inverse_fourier_transform((psd_average))
        spatial = spatial.real
        spatial = AstroImageProcessing.normalize(spatial)
        self.spatial = spatial
        return spatial

    def mean_filter(self):
        
        print("mean filter")
        #### Apply mean filter substraction to remove noise
        h,w = self.spatial.shape
        spatial_elipse = np.absolute(AstroImageProcessing.apply_mean_mask_subtraction(self.spatial,self.mean_f))
        spatial_elipse=spatial_elipse[1:h-1,1:w-1]
        

        self.spatial_elipse=AstroImageProcessing.normalize(detect_and_remove_lines(spatial_elipse)) * 65535

    
    def clip(self):
        print("clip")
        #### Clip image according to filters inputs
        self.spatial_elipse_filtered = (np.clip(self.spatial_elipse.copy(), self.min_value,self.max_value) - self.min_value)/(self.max_value-self.min_value)

        return self.spatial_elipse_filtered


    def find_ellipse(self):
        print("find_ellipse")
        spatial_elipse_filtered = (255*self.spatial_elipse_filtered).astype(np.uint8)
        print("find ellipse",spatial_elipse_filtered.min(),spatial_elipse_filtered.max())
        contours = find_contours(spatial_elipse_filtered)
        (ellipse, self.major_axe, self.minor_axe, self.angle_rad, self.focus1, self.focus2) = find_ellipse(contours[0])
        image2 = cv2.ellipse(spatial_elipse_filtered.copy(),ellipse,255, 1)
        return image2
    #show_image(image2, "Ellipse", st)

    def get_minus_major_star(self):
        #### Calculate perpendicular line from the ellipse main axis
        self.x_C = self.spatial_elipse.shape[1]/2
        self.y_C = self.spatial_elipse.shape[0]/2
        (self.m,p) = calculate_line((self.focus1[0],self.focus1[1]),(self.focus2[0],self.focus2[1]))
        (m_perp,p_perp) = calculate_perp(self.m, (self.spatial_elipse.shape[0]/2, self.spatial_elipse.shape[1]/2))

        #### Get image values along this line
        vectors = []
        for variance in range(-10,10):
            
            vectors.append(get_vector_from_direction(self.spatial_elipse,m_perp*(1+variance/100),(self.x_C,self.y_C),2*int(self.minor_axe)))
        vectors = np.array(vectors)
        vec = sum(vectors)/len(vectors)

        #### Use these values to extrapole central peak contribution and remove it from the image
        erased_image,central_disk = erase_principal_disk(self.spatial_elipse.copy(), vec)
        mean = erased_image.mean()
        erased_image = (np.clip(erased_image, mean*3,65535))
        erased_image = (erased_image-erased_image.min())*(erased_image.max()-erased_image.min())*65535
        cv2.circle(erased_image, (int(self.x_C),int(self.y_C)), self.radius, 0,-1)
        self.erased_image = erased_image

        
        return erased_image
    

    def isolate_peaks(self):
        (x,y,x2,y2)=detect_peaks(self.erased_image)
        result = self.erased_image.copy()
        h,w = self.spatial.shape
        result = result[1:h-1,1:w-1]
        cv2.circle(result,(x2,y2),2,result.max()*1.1,-1)
        cv2.circle(result,(x,y),2,result.max()*1.1,-1)
        return result



    def analyze_peaks(self):
        #### Slice the image along the elipse main axe
        curve = slice_from_direction(cv2.GaussianBlur(self.erased_image, (5, 5), 0),self.m, (self.x_C,self.y_C))

        #### Find peaks using gradients
        peaks,grads = find_peaks(curve)


        if len(peaks)>=2:
            peaks = peaks[0:2]
            dist1 = 0.099*(abs(curve[peaks[1][0]][0]))
            dist2 = 0.099*(abs(curve[peaks[0][0]][0]))
           # st.header(f"Distance calculated : {dist1},{dist2}, {(dist1+dist2)/2}")

        #### Find peaks using max values along x and -x axis

        i=0
        left_max={}
        right_max={}
        while curve[i][0]<0:
            left_max[curve[i][1]]=curve[i][0]
            if (i+len(curve)//2)<len(curve):
                right_max[curve[i+len(curve)//2][1]]=curve[i+len(curve)//2][0]
            i+=1
        
        lm = sorted(left_max.keys(), reverse=True)
        lr = sorted(right_max.keys(), reverse=True)
        """print(left_max[lm[0]], right_max[lr[0]])
        print(left_max[lm[1]], right_max[lr[1]])
        print(left_max[lm[2]], right_max[lr[2]])"""
        #st.header(f"Distance calculated : {left_max[lm[0]]},{right_max[lr[0]]}, {0.099*(abs(left_max[lm[0]])+abs(right_max[lr[0]]))/2}")


        #### Display

        #st.header("Analyse des pics dans la direction principale de l'ellipse")
        x = [item[0] for item in curve]
        y = [item[1] for item in curve]
        #fig, ax = plt.subplots()
        #ax.plot(x,y)
        lines = []
        for i in peaks:
            lines.append(curve[i[0]][0])
            #ax.axvline(x=curve[i[0]][0], color='r', linestyle='--')
        #st.pyplot(fig)
        
        return(x,y,lines, dist1, dist2, lm, lr)

        #fig, ax = plt.subplots()
        #ax.plot(x[1:-1],grads)
        for i in peaks:
            ax.axvline(x=i[0], color='r', linestyle='--')
        
        #st.pyplot(fig)