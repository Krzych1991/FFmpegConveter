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
    commands.append("-vcodec h264")
    commands.append("-vprofile high")
    commands.append("-preset superfast")
    commands.append("-threads 0")
    commands.append("-acodec ac3")
    commands.append("-map 0:v")
    commands.append("-map 0:a")
    commands.append("-stats")

    length = getLength(path)
    size = os.path.getsize(path)
    parts = 1 + (size / 1500000000)
    pathSRT = changeExtension(path, "srt")

    if (size / length) > 1200000:
        commands.append("-crf 31")
    if (size / length) > 900000:
        commands.append("-crf 29")
    if (size / length) > 600000:
        commands.append("-crf 27")
    elif (size / length) > 450000:
        commands.append("-crf 25")

    if parts <= 1:
        outputPath = createOutputPath(path)
        outputPath = changeExtension(outputPath, "mkv")
        commands.append("\"" + outputPath + "\"")
        if os.path.isfile(pathSRT):
            shutil.copyfile(pathSRT, createOutputPath(pathSRT))
    else:
        partLength = length / parts
        outputPath = createOutputPath(path, "%d")
        outputPath = changeExtension(outputPath, "mkv")
        commands.append("-segment_time " + str(partLength))
        commands.append("-f segment")
        commands.append("\"" + outputPath + "\"")
        if os.path.isfile(pathSRT):
            for i in range(0, parts):
                shutil.copyfile(pathSRT, createOutputPath(pathSRT, i))

    executeCommands(commands)

