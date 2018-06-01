#! /usr/bin/env python3
###############################################################################
# 
# Project: dem_ssara.py
# Author: Falk Amelung
# Created: 3/2018
#
###############################################################################


import os
import sys
import glob
import time
import argparse
import warnings
import shutil
import subprocess
import _readfile as readfile
import messageRsmas

import argparse

EXAMPLE = '''example:
  dem_rsmas.py  $SAMPLES/GalapagosT128SenVVD.template

      uses sentinelStack.boundingBox to generate a dem in DEM folder as dem.py requires integer degrees

      options:
           sentinelStack.demMethod = ssara [default: bbox]

      subtracts/adds ` 0.5 degree and then rounds to full integer

      '-1 0.15 -91.3 -90.9' -- >'-2 1 -92 -90

     work for islands where zip files may be missing
'''

##########################################################################


def create_dem_parser():
    parser = argparse.ArgumentParser(
        description='Implementing SSARA, ISCE, and more? options in DEM.\nDefault is to run ISCE')

    parser.add_argument(
        'custom_template_file',
        nargs='?',
        help='custom template with option settings.\n')
    parser.add_argument(
        '--ssara',
        dest='ssara',
        action='store_true',)
    parser.add_argument(
        '--new',
        dest='new',
        action='store_true',
        help='test option')

    return parser


def command_line_parse():
    parser = create_dem_parser()
    inps = parser.parse_args()
    inps.isce = True

    if inps.ssara:
        inps.isce = False
    return inps


def call_ssara_dem():
    print('you have started ssara!')

    print('now you are leaving ssara!')


def call_isce_dem(custom_template):

    bbox = custom_template['sentinelStack.boundingBox']
    bbox = bbox.strip("'")
    south = round(float(bbox.split()[0])-0.5)   # assumes quotes '-1 0.15 -91.3 -91.0'
    north = round(float(bbox.split()[1])+0.5)
    west = round(float(bbox.split()[2])-0.5)
    east = round(float(bbox.split()[3])+0.5)
  
    dembbox = str(int(south))+' '+str(int(north))+' '+str(int(west))+' '+str(int(east))

    # cmd = 'dem.py -a stitch -b '+demBbox+' -c -u https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'
    cmd = 'dem_rsmas_kawan.py -a stitch -b '+dembbox+' -c -u https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'
    messageRsmas.log(cmd)

    cwd = os.getcwd()

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print("Command failed. Exit code, StdErr:", exc.returncode, exc.output)
        sys.exit('Error produced by dem.py')
    else:
        # print("Success.        StdOut \n{}\n".format(output))
        if 'Could not create a stitched DEM. Some tiles are missing' in output:
            os.chdir('..')
            shutil.rmtree('DEM')
            sys.exit('Error in dem.py: Tiles are missing. Ocean???')

    xmlfile = glob.glob('demLat_*.wgs84.xml')[0]
    fin = open(xmlfile, 'r')
    fout = open("tmp.txt", "wt")
    for line in fin:
        fout.write(line.replace('demLat', cwd+'/demLat'))
    fin.close()
    fout.close()
    os.rename('tmp.txt', xmlfile)


def main(argv):
    # import pdb; pdb.set_trace()

    messageRsmas.log(' '.join(argv))
    inps = command_line_parse()
    # moved below to parse methods
    # parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
    #                                 epilog=EXAMPLE)
    # parser.add_argument('custom_template_file', nargs='?',
    #                    help='custom template with option settings.\n')
    # inps = parser.parse_args()

    custom_template = readfile.read_template(inps.custom_template_file)

    # import pdb;
    # pdb.set_trace()
    if os.path.isdir('DEM'):
        shutil.rmtree('DEM')
    os.mkdir('DEM')
    os.chdir('DEM')

    # cwd = os.getcwd()

    if 'sentinelStack.demMethod' not in custom_template.keys():
        custom_template['sentinelStack.demMethod'] = 'bbox'

    if custom_template['sentinelStack.demMethod'] == 'bbox' and inps.ssara:
        call_ssara_dem()
    if inps.new:
        print('nice job kawan! You aren\' dumb!')
    if custom_template['sentinelStack.demMethod'] == 'bbox' and inps.isce:
        print('you started isce')
        call_isce_dem(custom_template)
        print('you finished isce')
   
    else:
        sys.exit('Error unspported demMethod option: '+custom_template['sentinelStack.demMethod'])
    
    print('\n###############################################')
    print('End of dem_rsmas.py')
    print('################################################\n')

###########################################################################################


if __name__ == '__main__':
    main(sys.argv[:])
