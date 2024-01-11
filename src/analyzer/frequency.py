
from image_utils.image_utils import calculate_line, calculate_perp, detect_and_remove_lines, erase_principal_disk, \
                             find_contours,find_ellipse,get_vector_from_direction, find_peaks, slice_from_direction, detect_peaks,find_brightest_pixel,angle_with_y_axis
from image_utils.processing import AstroImageProcessing
from structure.message_queue import Message_Queue
import numpy as np
import cv2

class FrequencyAnalyzer:

    def __init__(self):
        self.min_value = 3000
        self.max_value = 40000
        self.mean_f = 3
        self.radius=2
        self.number_of_images = 10


    def psd(self, images):
        fouriers = []
        psd = []
        n = int(self.number_of_images *len(images)/ 100)
        for im in images[0:n]:
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
        min_vec = 1000
        for variance in range(-10,10):
            vec = get_vector_from_direction(self.spatial_elipse,m_perp*(1+variance/100),(self.x_C,self.y_C),int(2*self.minor_axe))
            if len(vec)<min_vec:
                min_vec = len(vec)
            vectors.append(vec)
        
        print("vectors")
        vectors = np.array(vectors[:][:min_vec])
        print(" after np vectors")

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
        """print(curve)
        #curve_1 = curve[0:len(curve)//2]
        #curve_2 = curve[0:len]

        negative_values = curve[curve[:, 0] < 0]
        positive_values = curve[curve[:, 0] >= 0]
        

        peaks_n,grads = find_peaks(negative_values)
        peaks_p,grads = find_peaks(positive_values)

        peaks = find_peaks(curve)

        print(peaks)


        if len(peaks)>=2:
            peaks = peaks[0:2]
            dist1 = (abs(curve[int(peaks[1][0]),0]))
            dist2 = (abs(curve[int(peaks[0][0]),0]))
           # st.header(f"Distance calculated : {dist1},{dist2}, {(dist1+dist2)/2}")"""

        #### Find peaks using max values along x and -x axis
        left_max = 0 
        right_max = 0
        left_max_index=-1
        right_max_index = -1

        for i in range(len(curve)):
            if curve[i][0]<0:
                if left_max< curve[i][1]:
                    left_max = curve[i][1]
                    left_max_index = i
            if curve[i][0]>0:
                if right_max< curve[i][1]:
                    right_max = curve[i][1]
                    right_max_index = i
            
        peaks=[[left_max_index, left_max],[right_max_index,right_max]]
        dist1 = (abs(curve[peaks[1][0]][0]))
        dist2 = (abs(curve[peaks[0][0]][0]))
        #st.header(f"Distance calculated : {left_max[lm[0]]},{right_max[lr[0]]}, {0.099*(abs(left_max[lm[0]])+abs(right_max[lr[0]]))/2}")
        #
        test=cv2.GaussianBlur(self.erased_image, (7, 7), 0)
        #test = self.erased_image.copy()
        
        
        
        x1, y1= find_brightest_pixel(test)
        cv2.circle(test,(x1,y1),int(self.major_axe/2),0,-1)
        test2 = test.copy()
        points=[]
        brightest = -1
        X = Y = n_points = 0
        for i in range(10):
            a,b = find_brightest_pixel(test2)
            if brightest<0:
                brightest=test2[b,a]
            print(test2[b,a])
            if test2[b,a]>0.5*brightest:
                points.append([a,b, test2[b,a]])
                X+=a
                Y+=b
                n_points+=1
            cv2.circle(test2,(a,b),1,0,-1)
        print(points)
        

        points=np.array(points)
        sum_brightness = np.sum(points[:,2])
        X=0
        Y=0
        tot=0
        for p in points : 
            f = p[2]/sum_brightness
            X+=p[0]*f
            Y+=p[1]*f
            tot+=f
        X = X/tot
        Y = Y/tot
        print(X,Y)
        dist = ((X - self.x_C)**2 + (Y-self.y_C)**2)**0.5
        print(dist*0.099)
        

        import imutils
        test3=(AstroImageProcessing.normalize(self.erased_image)*255).astype(np.uint8)
        contours = cv2.findContours(AstroImageProcessing.to_int8(test3), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(contours)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        result=[]
        for cnt in cnts[0:2]:
            cv2.drawContours(self.erased_image,[cnt],0,self.erased_image.max(),1)
            M = cv2.moments(cnt)
            ax1 = int(M["m10"] / M["m00"])
            ay1 = int(M["m01"] / M["m00"])
            dist1 = 0.099 * ((ax1 - self.x_C)**2 + (ay1-self.y_C)**2)**0.5
            result.append(dist1)
            print("Dist with contours : ", dist1)
        print("average dist : ", (result[0]+result[1])/2)


        x2,y2 = find_brightest_pixel(test)
        print(x1,y1,x2,y2)

        angle = angle_with_y_axis(x1,y1,x2,y2)
        dist1 = ((x1 - self.x_C)**2 + (y1-self.y_C)**2)**0.5
        dist2 = ((x2 - self.x_C)**2 + (y2-self.y_C)**2)**0.5
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
        lm = lr = 0
        return(x,y,lines, dist1, dist2, lm, lr, angle)
