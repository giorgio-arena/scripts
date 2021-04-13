import argparse
import sys
import traceback
from io import BytesIO
from PIL import Image
from zipfile import ZipFile

def main():
	# Argument parsing
	parser = argparse.ArgumentParser(description='Compress all images in a .cbz archive by a chosen percentage')
	parser.add_argument('--input', dest='input_filename', required=True, help='Filename of the input .cbz archive')
	parser.add_argument('--output', dest='output_filename', default='', help='Defaults to input_filename + \'_compressed.cbz\'')
	parser.add_argument('--quality', dest='compress_quality', default=50, help='Compress percentage (defaults to 50)', type=int)

	args = parser.parse_args()

	input_filename   = args.input_filename
	output_filename  = args.output_filename
	compress_quality = args.compress_quality

	# Arguments validation
	if input_filename[-4:] != '.cbz':
		raise TypeError("Wrong file extension")
	if (compress_quality < 1) or (compress_quality > 100):
		raise TypeError("Wrong compress quality, must be between 1 and 100")
	if output_filename == '':
		output_filename = input_filename[:-4] + '_compressed.cbz'

	# Get all images from archive, compress and save them to memory
	compressed = { 'filename': [], 'data': [] }
	try:
	    with ZipFile(input_filename) as archive:
	        for entry in archive.infolist():
	            with archive.open(entry) as file:
	                compressed['filename'].append(file.name)
	                compressed['data'].append(BytesIO())

	                if (file.name[-4:] == '.jpg') or (file.name[-5:] == 'jpeg'):
	                    Image.open(file).convert('RGB').save(compressed['data'][-1], 'JPEG', optimize=True, quality=compress_quality)
	                elif file.name[-4:] == '.png':
	                    Image.open(file).save(compressed['data'][-1], 'PNG')
	                else:
	                    print(file.name + ": File extension unsupported. Skipping")
	except:
	    traceback.print_exc()
	    exit()

	# Combine all the compressed images into a new archive
	out_file = ZipFile(output_filename,  mode='w')
	for i in range(len(compressed['filename'])):
	    out_file.writestr(compressed['filename'][i], compressed['data'][i].getvalue())

if __name__ == "__main__":
    main()