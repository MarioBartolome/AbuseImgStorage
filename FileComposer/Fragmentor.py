'''
Author: Mario Bartolome
Date: 16/04/2018

This program will fragment an input file to smaller pieces that could be uploaded to any free image storage service
without really taking any space on your account, as the service will recognize those as pictures.
'''

import random
import hashlib
import pickle
from collections import OrderedDict
import sys, os


HEADERS = [b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00', b'\xff\xd8\xff\xe1\x00\x10\x45\x78\x69\x66\x00']
HEADER_SIZE = 11

PREVIEW_HEX = 'imtest'

EOI = b'\xff\xd9'
EOI_SIZE = 2

MIN_fPICTURE_SIZE = 2048 * 1024
MAX_fPICTURE_SIZE = 5120 * 1024


def fragment(file):
	with open(file, 'rb') as f:
		full_digest = OrderedDict()
		fragment_number = 0

		# Chunking file
		fname, file_ext = os.path.splitext(os.path.basename(file))
		file_path = os.path.dirname(file)
		preview_hex_buffer = open(os.path.join(os.path.dirname(__file__), PREVIEW_HEX,), 'rb').read()
		print('[i] Splitting file...')
		for chunk in iter(lambda: f.read(random.randint(MIN_fPICTURE_SIZE, MAX_fPICTURE_SIZE)), b''):
			m = hashlib.sha256()
			filename = str(fragment_number) + ' - ' + fname + '.jpeg'
			with open(file_path + '/' + filename, 'wb') as w:
				w.write(HEADERS[random.randint(0, len(HEADERS)-1)])
				w.write(preview_hex_buffer)
				w.write(EOI)
				w.write(chunk)


			# Updates: fragment number and the full digest for reconstruction purposes
			with open(file_path + '/' + filename, 'rb') as w:
				m.update(w.read())
			d = m.digest()
			full_digest[fragment_number] = [filename, d]
			fragment_number += 1
			print('[*] Chunk created with name: ' + filename)
		# Build reconstruction db
		print('[i] Creating reconstruction database...')
		with open(file_path + '/' + fname + '.db', 'wb') as w:
			w.write(HEADERS[random.randint(0, len(HEADERS)-1)])
			w.write(preview_hex_buffer)
			_, full_digest['ext'] = os.path.splitext(file)
			pickle.dump(full_digest, w, pickle.HIGHEST_PROTOCOL)
			w.write(EOI)
		print('[*] Reconstruction db created')


def reconstruct(db):
	print('[i] Reading reconstruction database...')
	with open(db, 'rb') as dbf:
		reconstruction_db = pickle.loads(removeHeadEOI(dbf))
		ext = reconstruction_db.pop('ext')
		print('[*] Database ready')
		db_path = os.path.dirname(db)
		filename = os.path.splitext(os.path.basename(db))[0]
		with open(db_path + '/' + 'Reconstructed - ' + filename + ext, 'wb') as w:
			print('[i] Joining files...')
			for k, file_info in reconstruction_db.items():
				try:
					with open(db_path + '/' + file_info[0], 'rb') as f:
						# Check file integrity
						m = hashlib.sha256()
						m.update(f.read())
						if file_info[1] != m.digest():
							print('Something went wrong while reconstructing file: ' + file_info[0] + ' it seems to have changed!')
							sys.exit(1)

						# Reconstruct the file
						f.seek(0,0)
						w.write(removeHeadEOI(f))
				except FileNotFoundError:
					print("Hummm... I could not find the following file: " + db_path + '/' + file_info[0])
					return False

			print('[*] Files joined!')
			print('[*] Reconstructed file with name: recovered - ' + filename + ext)
			return True


def removeHeadEOI(f):
	buffer = f.read()
	buffer = buffer[HEADER_SIZE + len(open(os.path.join(os.path.dirname(__file__), PREVIEW_HEX,), 'rb').read()) + EOI_SIZE:]
	return buffer


def checkIntegrity(original, reconstructed):
	print('[i] Checking files integrity...')

	with open(original, 'rb') as o:
		with open(reconstructed, 'rb') as r:
			m_o = hashlib.sha256()
			m_r = hashlib.sha256()

			m_o.update(o.read())
			m_r.update(r.read())
			if (m_o.digest() == m_r.digest()):
				print('[*] Both files are equal!')
			else:
				print('[!] ERROR: The files differ!')


if __name__ == '__main__':
	args_no = len(sys.argv)
	if args_no == 2:
		if sys.argv[1].endswith('.db'):
			if(reconstruct(sys.argv[1])):
				print('Reconstruction finished successfully')
		else:
			fragment(sys.argv[1])
			print('Fragmentation finished successfully')
	elif args_no == 3:
		checkIntegrity(sys.argv[1], sys.argv[2])
	else:
		print('[!] USAGE: python3 Fragmentor.py FileToFragment/DBToReconstruct')
