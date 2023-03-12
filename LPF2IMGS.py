from cmath import pi
import os
from matplotlib import image
import numpy as np
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import ffmpeg as fp
import settings

# setting for load input images
imageNum = len([f for f in os.listdir(settings.inputDIR) if f.endswith(settings.EXT) and os.path.isfile(os.path.join(settings.inputDIR, f))])
filePath = settings.inputDIR + '/{}'.format(0) + settings.EXT

firstImage = cv2.imread(filePath,cv2.IMREAD_UNCHANGED).astype(np.float32)

# LPF definition
def MovingAverage():

    # make output directory
    os.makedirs(settings.outputDIR + "/MovingAverage",exist_ok=True)

    # LPF init
    FPS = imageNum * settings.inputFreq
    dt = 1.0 / settings.encodeFPS
    time = 0.0
    renderedFrames = 0
    count = 0

    # apply LPF
    while settings.renderDuration > time :

        # setup output buffer
        output = np.zeros((firstImage.shape[0],firstImage.shape[1],firstImage.shape[2])).astype(np.float32)

        # set sum interval
        interval = 1/settings.CFF

        t = 0.0
        c = 0
        while interval > t:    
            print(str((int)((time - t) * FPS) % imageNum ) + "/", end="", flush=True)

            output += cv2.imread(settings.inputDIR + '/{}'.format((int)((time - t) * FPS) % imageNum ) + settings.EXT ,cv2.IMREAD_UNCHANGED).astype(np.float32)

            t += 1 / ( imageNum * settings.inputFreq )
            c += 1

        # mean
        output_BGR = output / c

        # save image
        cv2.imwrite(settings.outputDIR + "/MovingAverage/output_{:0=4}.exr".format(renderedFrames + 1), output_BGR.astype(np.float32))
        renderedFrames += 1
        print("\nPrint Output : ", renderedFrames)

        time += dt
        count += 1

def RLC():
    # make output directory
    os.makedirs(settings.outputDIR + "/RLC",exist_ok=True)

    # LPF init
    FPS = imageNum * settings.inputFreq
    dt =min(1.0 / settings.encodeFPS , 1.0 / FPS)
    time = 0.0
    renderedFrames = 0
    count = 0

    # setup output buffer
    output = np.zeros((firstImage.shape[0],firstImage.shape[1],firstImage.shape[2])).astype(np.float32)

    # RLC paramater setting
    C = 1/((2*np.pi*settings.fc)**2*settings.L)
    R=1/settings.Q*np.sqrt(settings.L/C) / (2*np.pi)

    # Buffer setup
    a = np.zeros((firstImage.shape[0],firstImage.shape[1],firstImage.shape[2])).astype(np.float32)
    vel = np.zeros((firstImage.shape[0],firstImage.shape[1],firstImage.shape[2])).astype(np.float32)

    # LPF sequence
    while settings.renderDuration > time :

        if time * settings.encodeFPS >= renderedFrames :
            # save image
            output_BGR = output
            cv2.imwrite(settings.outputDIR + "/RLC/output_{:0=4}.exr".format(renderedFrames + 1), output_BGR.astype(np.float32))
            renderedFrames += 1
            print("\nPrint Output : ", renderedFrames)

        # show progress
        print(str((int)(time * FPS) % imageNum ) + "/", end="", flush=True)

        # load input image
        inputImage = cv2.imread(settings.inputDIR  + '/{}'.format((int)(time * FPS) % imageNum ) + settings.EXT ,cv2.IMREAD_UNCHANGED).astype(np.float32)
        # set state buffer
        prevOut = output.copy()

        # apply LPF
        a = (1/C * (inputImage - prevOut) - vel * R) / settings.L
        vel = a * dt
        output = prevOut + vel * dt

        time += dt
        count += 1

if settings.LPFMode == "MovingAverage":
    MovingAverage()
elif settings.LPFMode == "RLC":
    RLC()


# make output Movie
stream = fp.input(settings.outputDIR + "/" + settings.LPFMode + "/output_%04d" + settings.EXT, framerate=settings.encodeFPS)
stream = fp.output(stream, settings.outputDIR + "/" + settings.LPFMode + "/output.mp4",pix_fmt='yuv420p')
fp.run(stream)