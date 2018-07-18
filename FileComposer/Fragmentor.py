"""
Author: Mario Bartolome
Date: 16/04/2018

This program will fragment an input file to smaller pieces that could be uploaded to any free image storage service
without really taking any space on your account, as the service will recognize those as pictures.
"""

import random
import hashlib
import pickle
from collections import OrderedDict
import sys
import os
import argparse


HEADERS = [b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00', b'\xff\xd8\xff\xe1\x00\x10\x45\x78\x69\x66\x00']
HEADER_SIZE = 11

PREVIEW_HEX = 'imtest'

EOI = b'\xff\xd9'
EOI_SIZE = 2


def fragment(args):
	file = args.file
	MIN_fPICTURE_SIZE = args.MIN_SIZE
	MAX_fPICTURE_SIZE = args.MAX_SIZE

	try:
		with open(file, 'rb') as f:
			full_digest = OrderedDict()
			fragment_number = 0

			# Chunking file
			fname, file_ext = os.path.splitext(os.path.basename(file))
			file_path = os.path.dirname(file)
			preview_hex_buffer = open(os.path.join(os.path.dirname(__file__), PREVIEW_HEX,), 'rb').read()
			print('[i] Splitting file...')
			for chunk in iter(lambda: f.read(random.randint(MIN_fPICTURE_SIZE * 1024**2, MAX_fPICTURE_SIZE * 1024**2)), b''):
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
	except FileNotFoundError:
		print("Sorry, I could not find " + args.file, file=sys.stderr)


def reconstruct(args):
	db = args.file
	try:
		with open(db, 'rb') as dbf:
			print('[i] Reading reconstruction database...')
			reconstruction_db = pickle.loads(remove_head_EOI(dbf))
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
							f.seek(0, 0)
							w.write(remove_head_EOI(f))
					except FileNotFoundError:
						print("Hummm... I could not find the following file: " + db_path + '/' + file_info[0])
						return False

				print('[*] Files joined!')
				print('[*] Reconstructed file with name: Reconstructed - ' + filename + ext)
				return True
	except FileNotFoundError:
		print("Sorry, I could not find " + args.file, file=sys.stderr)



def remove_head_EOI(f):
	buffer = f.read()
	buffer = buffer[
	         HEADER_SIZE + len(
		         open(os.path.join(os.path.dirname(__file__), PREVIEW_HEX,), 'rb').read()
	         ) + EOI_SIZE:
	         ]
	return buffer


def check_integrity(args):
	original = args.file[0]
	reconstructed = args.file[1]
	print('[i] Checking files integrity...')

	with open(original, 'rb') as o:
		with open(reconstructed, 'rb') as r:
			m_o = hashlib.sha256()
			m_r = hashlib.sha256()

			m_o.update(o.read())
			m_r.update(r.read())
			if m_o.digest() == m_r.digest():
				print('[*] Both files are equal!')
			else:
				print('[!] ERROR: The files differ!')


if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(description='Give a file to chunk, a db next to chunks to reconstruct the '
	                                                 'original one, or two files to check integrity!')

	subparsers = arg_parser.add_subparsers(help='sub-command help')

	chunk_parser = subparsers.add_parser('chunk',
	                                     help='chunk file to image-like pieces')
	chunk_parser.add_argument('file',
	                          metavar='FILE',
	                          help='the file to chunk.',
	                          type=str
	                          )
	chunk_parser.add_argument('-m',
	                        '--min-size',
	                          dest='MIN_SIZE',
	                          help='the minimum size for the chunks to create. In MB, defaults to 2MB',
	                          type=int,
	                          default=2)
	chunk_parser.add_argument('-M',
	                          '--max-size',
	                          dest='MAX_SIZE',
	                          help='the maximum size for the chunks to create. In MB, defaults to 5MB',
	                          type=int,
	                          default=5)

	chunk_parser.set_defaults(func=fragment)


	reconstruction_parser = subparsers.add_parser('reconstruct',
	                                              help='reconstructs the original from the files next '
	                                                                  'to the db')
	reconstruction_parser.add_argument('file',
	                                   metavar='FILE',
	                                   help='the db file to reconstruct.',
	                                   type=str
	                                   )
	reconstruction_parser.set_defaults(func=reconstruct)


	check_integrity_parser = subparsers.add_parser('check',
	                                               help='checks the integrity of the reconstructed file, '
	                                                             'compared to the original one')

	check_integrity_parser.add_argument('file',
	                                    metavar='FILE_1 FILE_2',
	                                    nargs=2,
	                                    help='the two files to compare.',
	                                    type=str
	                                    )
	check_integrity_parser.set_defaults(func=check_integrity)


	args = arg_parser.parse_args()
	if not 'func' in args:
		arg_parser.print_help()
		raise AttributeError('I need something to work with...')

	if 'chunk' in args and args.MIN_SIZE > args.MAX_SIZE:
		chunk_parser.print_help()
		raise ValueError('Minimum size cannot be bigger than Maximum size...')

	args.func(args)
