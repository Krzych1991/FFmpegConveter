import os, sys, subprocess

def getLength(input_video):
    result = subprocess.Popen('ffprobe -i "' + input_video +'" -show_entries format=duration -v quiet -of csv="p=0"', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()
    return float(output[0])

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

for path in sys.argv[1:]:
    commands = []
    commands.append("ffmpeg")
    commands.append("-i \"" + path + "\"")
    commands.append("-vcodec h264")
    commands.append("-vprofile high")
    
    length = getLength(path)
    maxrate = int((8 * 2000000) / length)
    commands.append("-maxrate " + str(maxrate) + "k")
    commands.append("-bufsize 64k")
    
    commands.append("-preset superfast")
    commands.append("-threads 0")
    commands.append("-acodec ac3")

    filepath, filename = os.path.split(path)
    filepath = filepath + "/convert/";
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    commands.append("\"" + filepath + filename + "\"")
    
    #filepath, file_extension = os.path.splitext(path)
    #commands.append("\"" + filepath + "1" + file_extension + "\"")
    
    cmd = ' '.join(commands)
    print cmd
    os.system(cmd)
    
input("Press Enter to continue...")
