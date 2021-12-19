from django.db import models

import os
import numpy as np
from django.conf import settings
import logging
import cv2

logger = logging.getLogger(__name__)

# Create your models here.


class Picture(models.Model):
    picture = models.ImageField(upload_to="image/%Y/%m/%d")
    processed_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save()
        image = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), str(self.picture.url[1:]))
        img = cv2.imread(f'{image}', cv2.IMREAD_UNCHANGED)
        print(img)
        print(type(img))
        print(img.shape)
        img_name = image.split('/')[-1]
        # logger.info('Original Dimensions : ', img.shape)
        scale_percent = 50  # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

        # resize image
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        logger.info(f'Resized Dimensions : {resized.shape}')
        new_location = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), f"uploads/resized/{img_name}")
        cv2.imwrite(new_location, resized)

        # First extraction
        image = cv2.imread(new_location)
        # logger.info(f"Reading File {new_location} with {image.shape} shape")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)[1]

        # Find contour and sort by contour area
        cnts = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # Find bounding box and extract ROI
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            ROI = image[y:y+h, x:x+w]
            logger.info(f"Result dimension {ROI.shape}")
            break
        new_location_2 = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), f"uploads/phone_part/{img_name}")
        cv2.imwrite(new_location_2, ROI)

        # Second extraction of ROI
        image = cv2.imread(new_location_2)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 179, 255, cv2.THRESH_BINARY)[1]

        # Find contour and sort by contour area
        cnts = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # Find bounding box and extract ROI
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            ROI = image[y:y+h, x:x+w]
            break
        new_location_3 = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), f"uploads/heat/{img_name}")
        cv2.imwrite(new_location_3, ROI)

        # Third extraction of second ROI
        img = cv2.imread(new_location_3)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # threshold input image using otsu thresholding as mask and refine with morphology
        ret, mask = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # put mask into alpha channel of result
        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask
        result = cv2.bitwise_and(result, result, mask=mask)
        result_location = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), f"uploads/result/{img_name}")
        cv2.imwrite(f'{result_location}', result)
        self.processed_image = f"/result/{img_name}"
        super().save()
