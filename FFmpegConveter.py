import argparse
import os
import pysrt
import shutil
import subprocess
import sys
import tempfile
import helper

def createOutputPath(path, suffix=None):
    filepath, filename = os.path.split(path)
    filename1, fileextension = os.path.splitext(filename)
    filepath = os.path.join('convert', filename1);
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    if suffix is not None:
        filename = filename1 + '_' + str(suffix) + fileextension;
    return os.path.join(filepath, filename)

def changeExtension(path, extension):
    filename, fileextension = os.path.splitext(path)
    return filename + '.' + extension

def getLength(input_video):
    result = subprocess.Popen('ffprobe -i "' + input_video +'" -show_entries format=duration -v quiet -of csv="p=0"', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = result.communicate()
    return float(output[0])

def executeCommands(commands):
    print "\n".join(commands), '\n'
    os.system(' '.join(commands))

def getCRF(Kbps):
    if Kbps < 450:
        return 0
    return int(min((Kbps - 450) / 125 + 25, 31))

def main(argv):
    parser = argparse.ArgumentParser(description='FFmpegConveter')
    parser.add_argument('-i', dest='input', required=True, help='input file', metavar='FILE')
    parser.add_argument('-s', dest='subtitlesSize', type=int , default=23)
    
    args = parser.parse_args()
    path = args.input
    subtitlesSize = args.subtitlesSize
    print 'Processing:\t', os.path.basename(path)
    
    commands = []
    commands.append('ffmpeg')
    commands.append('-i "' + path + '"')
    commands.append('-vcodec h264')
    commands.append('-vprofile high')
    commands.append('-preset superfast')
    commands.append('-threads 0')
    commands.append('-acodec ac3')
    commands.append('-map 0:v:0')
    commands.append('-map 0:a')
    commands.append('-fs 2100000000')
    
    length = getLength(path)
    size = os.path.getsize(path)
    pathSRT = changeExtension(path, 'srt')
    
    if not os.path.isfile(pathSRT):
        if not helper.query_yes_no('Subtitles not found, continue?'):
            quit()
    
    crf = getCRF((size / length) / 1000)
    if crf > 0:
        commands.append('-crf ' + str(crf))
    
    part = 1
    lengthParts = 0
    while lengthParts + (2 * part) < length:
        commandsT = list(commands)
        outputPath = createOutputPath(path, '_' + str(part))
        outputPath = changeExtension(outputPath, 'mkv')
        
        if os.path.isfile(pathSRT):
            with tempfile.NamedTemporaryFile(dir='tmp', suffix='.srt', delete=False) as tmpfile:
                subs = pysrt.open(pathSRT)
                subs.shift(seconds=-lengthParts)
                subs.save(tmpfile.name)
                commandsT.append('-vf "subtitles=\'' + os.path.relpath(tmpfile.name).replace('\\', '\\\\') + '\':force_style=\'Fontsize=' + str(subtitlesSize) + '\'"')
        
        commandsT.insert(1, '-ss ' + str(lengthParts))
        commandsT.append('"' + outputPath + '"')
        
        executeCommands(commandsT)
        lengthParts = lengthParts + getLength(outputPath) - 2
        part = part + 1

if __name__ == '__main__':
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    main(sys.argv)
