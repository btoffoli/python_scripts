from pytube import YouTube as YT # pytube==9.5.2
from sys import argv
from unidecode import unidecode

def remove_non_ascii(text):
	return unidecode(text)


print(len(argv))
file_input_name = argv[1] if len(argv) > 1 else 'youtubelinks.txt'
destination_path = argv[2] if len(argv) > 2 else '/tmp/'
prefix_file_name = ('%s - ' % argv[3]) if len(argv) > 3 else ''
count = 0
with open(file_input_name) as filesrc:
	for linelnk in filesrc.readlines():
		filename = None
		try:
			count += 1
			yt = YT(linelnk)
			video = max(filter(lambda st: st.mime_type == 'video/mp4' and st.resolution and st.includes_audio_track, yt.streams.fmt_streams), key=lambda x: int(x.resolution.replace('p', ''))+ x.fps)
			#video = yt.get('mp4', '720p')
			if video:
				print('Downloading %s....' % video.default_filename)
				video.download(destination_path)
			else:
				print('Download mp4 format not found: Name: %s Link: %s' % (filename, linelnk))
		except Exception as e:
			print('Download fail: Name: %s Link: %s' % (filename, linelnk))
			print(e)
