#!/usr/bin/python3

import argparse
import os

NOT_GSC_DIRS = [
	"base_images",
	".git"
]

SKIP_FILES = [
	".gitignore", 
	".gitkeep"
]
""" Get a list of all directories that are supposed to be game server containers.
"""
def get_all_gsc(base_dir="."):
	dirs = []
	for d in next(os.walk(base_dir))[1]:
		if not d in NOT_GSC_DIRS:
			dirs.append(d)
	return dirs

""" Check if a game server containers server_files dir is clean.
"""
def gsc_is_clean(gsc):
	for name in os.listdir(os.path.join(gsc, "server_files")):
		if not name in SKIP_FILES:
			return False
	return True

""" Remove all files and subdirectories in the given directory.
"""
def rm_dir_recursive(directory, skip=SKIP_FILES, verbose=None):
	for root, dirs, files in os.walk(directory, topdown=False):
		for name in files:
			if os.path.basename(name) in skip:
				continue
			if verbose:
				print("  -- deleting file " + os.path.join(root, name))
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
			if verbose:
				print("  -- deleting directory " + os.path.join(root, name))


""" Entry point
"""
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="""Clean a game server containers server_files. 
		!!! WARNING: "Cleaning" a game server container will DELETE ALL SERVER FILES, including 
		configurations and saves. !!! If you want to be sure not to delete something by accident, 
		use the --interactive flag.""")
	
	parser.add_argument("--interactive", "-i", action="store_const", const="interactive", 
		help="Ask before cleaning the directories.")
	parser.add_argument("--verbose", "-v", action="store_const", const="verbose",
		help="Show more verbose output")
	
	pgroup_gsc = parser.add_mutually_exclusive_group(required=True)
	pgroup_gsc.add_argument("--gsc", "-c", action="append", dest="gsc",
		help="The name of the game server container that should be cleaned")
	pgroup_gsc.add_argument("--all", "-a", action="store_const", const="all", 
		help="Clean all game server containers.")
	
	pargs = parser.parse_args()
	
	if pargs.all:
		pargs.gsc = get_all_gsc()
		print("Cleaning all game server containers.")
		print(pargs.gsc)
	
	for gsc in pargs.gsc:
		sf_path = os.path.join(gsc, "server_files")
		gsc_tag = "[" + gsc + "] "
		if len(gsc_tag) < 15:
			gsc_tag += " " * (15-len(gsc_tag))
			
		if not os.path.isdir(gsc):
			print(gsc_tag, "Gameserver ", gsc, " not found. Skipping ", sf_path)
		if not os.path.isdir(sf_path):
			print(gsc_tag, "Directory server_files does not exist. Skipping ", sf_path)
			continue
		
		if gsc_is_clean(gsc):
			print(gsc_tag, "Game server container is still clean. Skipping ", sf_path)
			continue
		
		if pargs.interactive:
			inp = input("Clean ", sf_path, "? This will delete all server files including saves. (y/n) ")
			if inp != "y":
				print("Not cleaning ", sf_path)
				continue
		
		print(gsc_tag, "Cleaning ", sf_path)
		rm_dir_recursive(sf_path, verbose=pargs.verbose)
		
