import os, sys, subprocess

def createOutputPath(path, suffix = None):
    filepath, filename = os.path.split(path)
    filepath = filepath + "/convert/";
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if suffix is not None:
        filename1, fileextension = os.path.splitext(filename)
        filename = filename1 + "_" + suffix + fileextension;
    return filepath + filename

def changeExtension(path, extension):
    filename, fileextension = os.path.splitext(path)
    return filename + "." + extension

def getLength(input_video):
    result = subprocess.Popen('ffprobe -i "' + input_video +'" -show_entries format=duration -v quiet -of csv="p=0"', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()
    return int(float(output[0]))

def executeCommands(commands):
    cmd = ' '.join(commands)
    print cmd
    os.system(cmd)

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

for path in sys.argv[1:]:
    commands = []
    commands.append("ffmpeg")
    commands.append("-i \"" + path + "\"")
    
    patrSRT = changeExtension(path, "srt")
    if os.path.isfile(patrSRT):
        commands.append("-f srt")
        commands.append("-i \"" + patrSRT +"\"")
        commands.append("-scodec ass")
        commands.append("-map 1")
    
    commands.append("-vcodec h264")
    commands.append("-vprofile high")
    commands.append("-preset superfast")
    commands.append("-threads 0")
    commands.append("-acodec ac3")
    commands.append("-map 0:v")
    commands.append("-map 0:a")

    length = getLength(path)
    size = os.path.getsize(path)
    parts = 1 + (size / 1000000000)

    if parts <= 1:
        outputPath = createOutputPath(path)
        outputPath = changeExtension(outputPath, "mkv")
        commands.append("\"" + outputPath + "\"")
    else:
        partLength = length / parts
        outputPath = createOutputPath(path, "%d")
        outputPath = changeExtension(outputPath, "mkv")
        commands.append("-segment_time " + str(partLength))
        commands.append("-f segment")
        #commands.append("-reset_timestamps 1")
        commands.append("\"" + outputPath + "\"")

    executeCommands(commands)
    
input("Press Enter to continue...")
