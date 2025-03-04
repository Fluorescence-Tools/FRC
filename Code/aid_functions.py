#helper functions for developmental functions and Gauss fitting
#Nicolaas van der Voort
#AG Seidel, 4 March, 2020
##issue: findPeaksLib increases dependance and lessens flexibility
##get rid of it and move depending functions.
import findPeaksLib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import os
import pickle
import shutil
from datetime import datetime

def pos2ROI(xpos, ypos, winSigma):
    """convert center position and width to ROI"""
    xstart = xpos - winSigma
    xstop = xpos + winSigma +1
    ystart = ypos - winSigma
    ystop = ypos + winSigma + 1
    #ROI is column major
    #ROI = np.array([ystart, xstart, ystop, xstop], dtype = np.int).transpose()
    #some confusion occurred whether data is row or column major, for row major:
    ROI = np.array([xstart, ystart, xstop, ystop], dtype = int).transpose()
    return ROI

def loadpickle(outname):
    with open(outname, 'rb') as f:
        return pickle.load(f)
    
def savepickle(data, outname):
    with open(outname, 'wb') as output:
        pickle.dump(data, output, 1)
        
def saveDict(dictionary, outfile):
    """save dict column-wise to file."""
    outdir = os.path.split(outfile)[0]
    trymkdir(outdir)
    keys = dictionary.keys()
    header = ''
    for key in keys:
        header += key + '\t'
    header += '\n'
    length = len(dictionary[key])
    with open(outfile, 'wt') as f:
        f.write(header)
        for i in range(length):
            line = ''
            for key in keys:
                line += str(dictionary[key][i]) + '\t'
            line += '\n'
            f.write(line)
            
def simplePTUmerge(infolder, outfolder = '', move = False):
    """copies all ptu files in subfolders of infolder to outfolder"""
    if outfolder == '':
        outfolder = os.path.join(infolder, 'all')
    print(outfolder)
    try:
        os.mkdir(outfolder)
        print('creating folder')
    except FileExistsError:
        pass
    folders = [f for f in os.listdir(infolder) if \
        os.path.isdir(os.path.join(infolder, f))]
    for folder in folders:
        subfolder = os.path.join(infolder, folder)
        files = os.listdir(subfolder)
        for file in files:
            if file.endswith('.ptu'):
                source = os.path.join(subfolder, file)
                destination = os.path.join(outfolder, file)
                # this avoids copying files twice
                if os.path.isfile(destination): 
                    continue
                if move:
                    shutil.move(source, destination)
                else:
                    shutil.copyfile(source, destination)
                
##########helper functions from Gauss Analysis Pipeline#########################
def cropAnI(image, ROI, ROISize, ROIpad = 0):
    """crop ROI from image
    ROI: roi parameters as taken from AnI, corner positions are taken
    ROISize: length of square ROI from Ani
    ROIpad (optional): enlarge ROI from AnI on all sides
    side of ROI has length: ROISize + 2 * ROIpad"""
    xshape, yshape = image.shape
    cornery, cornerx = ROI[[0, 2]].astype(np.int) - np.array([ROIpad, ROIpad])
    ROISize = ROISize + 2 * ROIpad
    if cornerx < 0 or cornery < 0 or cornerx + ROISize > xshape or cornery + ROISize > yshape:
        raise IndexError
    ROIsnip = image[cornerx: cornerx + ROISize, cornery: cornery + ROISize]
    return ROIsnip
    
def matchfiles(files, roifiles, ext = '_Red Photons.roi'):
    """matches a set of roifiles to their original ptu files based on names.
    Returns a list of filename pairs"""
    filepairs = []
    #copy files to avoid popping original list
    filescopy = files[:]
    for roifile in roifiles:
        for i in range(len(filescopy)):
            if filescopy[i][:-4] == roifile[:-len(ext)]:
                filepairs.append([filescopy.pop(i),roifile])
                break
    return filepairs
    

def genROI(im, ROIsize):
    """get single ROI around intensity max of image"""
    assert ROIsize % 2 == 0
    ROIside = ROIsize / 2
    smooth_im = findPeaksLib.smooth_image(im)
    xlen, ylen = im.shape
    maxpos = smooth_im.argmax()
    xpos, ypos = [maxpos // xlen, maxpos % xlen]
    ROI = np.array([xpos - ROIside, ypos - ROIside, xpos + ROIside, ypos + ROIside]).astype(np.int)
    return ROI

def crop(image, ROI):
    """crop ROI from image
    ROI: roi parameters as taken from getROI
    returns cropped image"""
    xshape, yshape, *_ = image.shape #*_ is wildcard in case of lifetime image
    if ROI[0] < 0 or ROI[1] < 0 or ROI[2] >= xshape or ROI[3] >= yshape:
        raise IndexError ('ROI outside of image borders')
    return image[ROI[0]: ROI[2], ROI[1]: ROI[3]]

def createPath(ffile):
    """creates path of ffile if it does not exist already"""
    path, file = os.path.split(ffile)
    try:
        os.mkdir(path)
    except FileExistsError: 
        pass
    return True
    
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx
    
def trymkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    
def backup_onExt(rootfolder, ext = '.csv', timestamp = None):
    #get single timestamp for all recursive files, same format as in Abberior-Tools
    if timestamp == None:
        dateTimeObj = datetime.now()
        timestamp = dateTimeObj.strftime("%Y-%b-%d-%H-%M-%S")
    ffiles = [os.path.join(rootfolder, file) for file in os.listdir(rootfolder)]
    for ffile in ffiles:
        if os.path.isfile(ffile):
            if ffile.endswith(ext):
                #make backup dir if it does not exits
                backupfolder = os.path.join(rootfolder, 'backup')
                trymkdir(backupfolder)
                #dst
                destination = os.path.join(backupfolder, os.path.split(ffile)[1][:-len(ext)]+timestamp+ext)
                shutil.copy(ffile, destination)
                print('backed up file %s' % ffile)
        elif os.path.isdir(ffile):
            if ffile.endswith('backup'):continue #avoid backing up backups
            backup_onExt(ffile, ext, timestamp)
    
########################plotting functions#####################################
def plotBitmapROI(bitmap, spotLst, title = ''):
    fig,ax = plt.subplots(1)
    ax.imshow(bitmap)
    #x index is the first index and refers to columns in image
    #y index is the seconf index and refers to rows in image
    for spot in spotLst:
        rect = patches.Rectangle((spot.ystart, spot.xstart), 
                                spot.ystop - spot.ystart,
                                spot.xstop - spot.xstart,
                                linewidth = 1, edgecolor = 'r', facecolor='none')
        ax.add_patch(rect)
        ax.plot(spot.posy, spot.posx, 'r.')
    ax.set_title(title)
    plt.show()