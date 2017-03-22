from pytube import YouTube as YT
from sys import argv
from unidecode import unidecode

def remove_non_ascii(text):
    return unidecode(text)


print(len(argv))
file_input_name = argv[1] if len(argv) > 1 else 'youtubelinks.txt'
destination_path = argv[2] if len(argv) > 2 else '/tmp/'
prefix_file_name = ('%s - ' % argv[3]) if len(argv) > 3 else ''

with open(file_input_name) as filesrc:
    for linelnk in filesrc.readlines():
        try:
            yt = YT(linelnk)
            #print(yt.get_videos())
            #print(yt.filename)
            #print(yt.get_videos())
            filename = remove_non_ascii(yt.filename)
            print('Downloading %s....' % filename)
            yt.set_filename('%s%s' %(prefix_file_name, filename))
            video = yt.filter('mp4')[-1]
            #video = yt.get('mp4', '720p')
            if video:
                video.download(destination_path)
            else:
                print('Download mp4 format not found: Name: %s Link: %s' % (filename, linelnk))
        except Exception as e:
            print('Download fail: Name: %s Link: %s' % (filename, linelnk))
            print(e)
    
