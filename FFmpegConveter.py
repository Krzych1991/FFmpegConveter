import os, shutil, sys, subprocess

def createOutputPath(path, suffix = None):
    filepath, filename = os.path.split(path)
    filename1, fileextension = os.path.splitext(filename)
    filepath = "convert/" + filename1 + "/";
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if suffix is not None:
        filename = filename1 + "_" + str(suffix) + fileextension;
    return filepath + filename

def changeExtension(path, extension):
    filename, fileextension = os.path.splitext(path)
    return filename + "." + extension

def getLength(input_video):
    result = subprocess.Popen('ffprobe -i "' + input_video +'" -show_entries format=duration -v quiet -of csv="p=0"', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()
    return float(output[0])

def executeCommands(commands):
    cmd = ' '.join(commands)
    print cmd
    os.system(cmd)
    
def getCRF(Kbps):
    if Kbps > 1200:
        return 31
    if Kbps > 900:
        return 29
    if Kbps > 600:
        return 27
    if Kbps > 450:
        return 25
    return 0

for path in sys.argv[1:]:
    print "Processing:\t", os.path.basename(path)
    
    commands = []
    commands.append("ffmpeg")
    commands.append("-i \"" + path + "\"")
    commands.append("-vcodec h264")
    commands.append("-vprofile high")
    commands.append("-preset superfast")
    commands.append("-threads 0")
    commands.append("-acodec ac3")
    commands.append("-map 0:v")
    commands.append("-map 0:a")
    commands.append("-stats")
    commands.append("-fs 1900000000")
    
    length = getLength(path)
    size = os.path.getsize(path)
    pathSRT = changeExtension(path, "srt")
    
    if os.path.isfile(pathSRT):
        print "Found subtiltes"
        commands.append("-vf \"subtitles='" + pathSRT.replace("\\", "\\\\").replace(":", "\\:") + "':force_style='Fontsize=23'\"")
    
    crf = getCRF((size / length) / 1000)
    if crf > 0:
        commands.append("-crf " + str(crf))
    
    part = 1
    lengthParts = 0
    while lengthParts + 3 < length:
        commandsT = list(commands)
        outputPath = createOutputPath(path, "_" + str(part))
        outputPath = changeExtension(outputPath, "mkv")
        commandsT.append("-ss " + str(lengthParts))
        commandsT.append("\"" + outputPath + "\"")
        executeCommands(commandsT)
        lengthParts = lengthParts + getLength(outputPath) - 1
        part = part + 1
