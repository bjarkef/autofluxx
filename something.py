#!/usr/bin/python2

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import glob

#import pdb; pdb.set_trace()

#template = cv2.imread('templatecolor.jpg')
#template = cv2.GaussianBlur(template, (5,5),0)
#graytemplate = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

orb = cv2.ORB_create(nfeatures=500)
#orig_psize = orb.getPatchSize()
#orb.setPatchSize(orig_psize)
#orb.setEdgeThreshold(0)

#kptemplate, destemplate = orb.detectAndCompute(template, None)

#orb.setPatchSize(orig_psize)
#orb.setMaxFeatures(500)
#orb.setScaleFactor(1.01)


cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

global cropped, roi

try:
	with open('crop.pickle', 'r') as f:
		roi = pickle.load(f)
		cropped = True
except IOError:
	cropped = False
	roi = [[0,0], [1920,1080]]

#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
#fgbg = cv2.BackgroundSubtractorMOG2(nShadowDetection=0)

def nothing(x):
	pass

#cv2.namedWindow('canny')
#cv2.createTrackbar('canny_min', 'canny', 90, 255, nothing)
#cv2.createTrackbar('canny_max', 'canny', 160, 255, nothing)



def mousecb(event, x, y, flags, param):
	global cropped, roi
	x = x*4
	y = y*4
	if event == cv2.EVENT_LBUTTONDOWN:
		roi[0] = [x,y]
		if cropped:
			cropped = False
			os.remove('crop.pickle')
	if event == cv2.EVENT_RBUTTONDOWN:
		if x < roi[0][0]:
			roi[1][0] = roi[0][0]
			roi[0][0] = x
		else:
			roi[1][0] = x
		
		if y < roi[0][1]:
			roi[1][1] = roi[0][1]
			roi[0][1] = y
		else:
			roi[1][1] = y
		cropped = True
		with open('crop.pickle', 'w') as f:
			pickle.dump(roi, f)
		
def setfeatures(x):
	print("Setting features: {0}".format(x))
	orb.setMaxFeatures(x)
	

cv2.namedWindow('contours', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('contours', mousecb)
cv2.createTrackbar('min_area', 'contours', 5000, 50000, nothing)
cv2.createTrackbar('features', 'contours', 500, 5000, setfeatures)

cv2.namedWindow('edges')
cv2.createTrackbar('sigma', 'edges', 75, 150, nothing)

while True:
	ret, frame = cap.read()
	if not ret: raise NameError("Cannot open video source")
	uncroppedgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	if cropped:
		gray = uncroppedgray[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
		frame = frame[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
#		print("cropping = {0}:{1}, {2}:{3}".format(roi[0][0],roi[1][0], roi[0][1],roi[1][1]))
	else:
		gray = uncroppedgray

#	gray = frame

	sigma = cv2.getTrackbarPos('sigma', 'edges')
	bfiltered = cv2.bilateralFilter(gray, 5, sigma, sigma)

	edges = cv2.adaptiveThreshold(bfiltered,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
#	canny = cv2.Canny(graycopy,
#		cv2.getTrackbarPos('canny_min', 'canny'),
#		cv2.getTrackbarPos('canny_max', 'canny'))
#	kernel = np.ones((7,7),np.uint8)
#	canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
#	canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
#	canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

	small = cv2.resize(edges, (0, 0), fx=0.25, fy=0.25, interpolation = cv2.INTER_AREA)
	#small = canny
	cv2.imshow('edges', small)

	im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
	
#	for c in contours:
#		print(cv2.contourArea(c))

	contours = [c for i, c in enumerate(contours) if hierarchy[0][i][2] == -1]
	contours = [x for x in contours if cv2.contourArea(x) > cv2.getTrackbarPos('min_area', 'contours')]
	contours = sorted(contours, key = lambda c : cv2.contourArea(c))

	cnt = None
#	if len(contours) > 0:
#		cnt = contours[0]
#		for c in contours:
#			if cv2.contourArea(c) > cv2.contourArea(cnt):
#				cnt = c

#		epsilon = 0.1 * cv2.arcLength(cnt, True)
#		approx = cv2.approxPolyDP(cnt, epsilon, True)
#		print('largest area = {0}, lines in s.c. = {1}'.format(cv2.contourArea(cnt), len(approx)))

	graycopy = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
	cv2.drawContours(graycopy, contours, -1, (0,255,0), 2)
	if cnt != None:
		cv2.drawContours(graycopy, [cnt], -1, (0,255,0), -1)

	quadraticcontours = []
	for c in contours:
		epsilon = 0.1 * cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, epsilon, True)
		if len(approx) == 4:
			cv2.drawContours(graycopy, [approx], 0, (255,0,255), 5)
			quadraticcontours.append(approx)

	print('number of quadratic contours = {0}'.format(len(quadraticcontours)))

	#small = cv2.resize(graycopy, (0, 0), fx=0.25, fy=0.25)
	cv2.imshow('contours', graycopy)

	
	for i,c in enumerate(quadraticcontours):
#		print('contour #{0}:'.format(i))
#		for p in c:
#			print(p[0])

		# Sort corners

#		print np.linalg.norm(c[0,0]-c[1,0])
		shortside=0
		side1 = np.linalg.norm(c[0,0]-c[1,0])
		side2 = np.linalg.norm(c[3,0]-c[0,0])
		if (side1 < side2):
#			print("not rotated")
			tl = c[0,0]
			tr = c[1,0]
			br = c[2,0]
			bl = c[3,0]
			shortside = int(side1)
		else:
#			print("rotated")
			tl = c[3,0]
			tr = c[0,0]
			br = c[1,0]
			bl = c[2,0]
			shortside = int(side2)


		x,y,w,h = cv2.boundingRect(c)
#		cimg = frame[y:y+h, x:x+w]
#		cimg = cv2.cvtColor(cimg, cv2.COLOR_GRAY2BGR)
#		cv2.circle(cimg, (tl[0]-x,tl[1]-y), 30, (255,0,255), 10)

		longside = int(shortside * 1.333)

		#pcimg = np.zeros((shortside, longside, 3), np.uint8)
		src = np.array([tl, tr, br, bl], np.float32)
		dst = np.array(
			[[0,0], [shortside-1, 0],
			[shortside-1,longside-1],
			[0, longside-1]],
			np.float32)

		M = cv2.getPerspectiveTransform(src, dst)
		warped = cv2.warpPerspective(frame, M, (shortside, longside))

		name = 'contour #{0}'.format(i)
		cv2.namedWindow(name, cv2.WINDOW_NORMAL)
		cv2.imshow(name, warped)
	


	#	fgmask = fgbg.apply(gray)
	#	cv2.imshow('frame', fgmask)
		cardtemps = list(glob.iglob('cards/*.jpg'))
		likelihoods=[]

		for ct in cardtemps:
			template = cv2.imread(ct)
			template = cv2.GaussianBlur(template, (5,5),0)
	
			scaledtemplate = cv2.resize(template, (shortside, longside))
	
			kptemplate, destemplate = orb.detectAndCompute(scaledtemplate, None)
			kpframe, desframe = orb.detectAndCompute(warped, None)
		
			bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
		
			if desframe == None: continue
	
			matches = bf.knnMatch(destemplate, desframe, k=2)
	#		matches = bf.match(destemplate, desframe)
	#		matches = sorted(matches, key = lambda x:x.distance)
		
		
		
			goodmatches = []
			for m,n in matches:
				if m.distance < 0.7*n.distance:
					goodmatches.append(m)
	
		
			if len(goodmatches)>10:
				src_pts = np.float32([ kptemplate[m.queryIdx].pt for m in goodmatches ]).reshape(-1,1,2)
				dst_pts = np.float32([ kpframe[m.trainIdx].pt for m in goodmatches ]).reshape(-1,1,2)
		
				matchesMask = None
				M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,1.0)
				if mask != None:
					matchesMask = mask.ravel().tolist()
				
		
				#if matchesMask != None and (sum(matchesMask) > 10):
				#
				#	h,w = template.shape
				#	pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
				#	dst = cv2.perspectiveTransform(pts,M)
		
					#cv2.polylines(gray,[np.int32(dst)],True,255,3, cv2.LINE_AA)
			else:
				matchesMask = [0] * len(goodmatches)

			likelihoods.append(sum(matchesMask))

		if len(likelihoods) > 0 and max(likelihoods) > 0:
			print("card {0} likelihoods: {1}".format(i, likelihoods))
			print("card {0} is probably: {1}".format(i, cardtemps[likelihoods.index(max(likelihoods))]))

#		draw_params = dict(
#		                   matchesMask = matchesMask, # draw only inliers
#		                   flags = 6)
#	
#		matchimg = cv2.drawMatches(scaledtemplate, kptemplate, warped, kpframe, goodmatches, None, **draw_params)
#		small = cv2.resize(matchimg, (0, 0), fx=0.5, fy=0.5)
##		cv2.imshow('match ', small)
#		
#		name = 'match #{0}'.format(i)
#		cv2.namedWindow(name, cv2.WINDOW_NORMAL)
#		cv2.imshow(name, matchimg)

	#	cv2.imshow('match', gray)
		#plt.imshow(matchimg)
		#plt.show()

	print("")

	key = cv2.waitKey(100) & 0xFF
	if key == ord('q'):
		break
	elif key == ord('p'):
		cv2.waitKey(0)

#	time.sleep(1)

cap.release()
cv2.destroyAllWindows()
