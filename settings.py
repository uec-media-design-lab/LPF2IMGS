# Directory where input imagesFramerate
inputDIR = "Render/SimpleScan"

# Directory where input images
outputDIR = "Result/SimpleScan"

# Extension of images
EXT = '.exr'

# Framerate of input images
inputFreq = 80.0

# Framerate of output images
encodeFPS = 60.0

# Duration of output images
renderDuration = 5.0 #[seconds]

# CFF
CFF = 40.0

# LPF Mode
# ["MovingAvarage", "RLC"]
# LPFMode = "MovingAvarage"
LPFMode = "RLC"
    
# settings for RLC
if LPFMode == "RLC":
    Q = 5
    L = 0.01
    fc = CFF / 2
