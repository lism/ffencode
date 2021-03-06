#!/usr/bin/env python

__author__ = 'Xia shine <changyao.xiahou@1905.com>'
__copyright__ = 'Copyright 2014, 1905 Technologies'

import sys
import os
import glob
import re
import os.path as path
from subprocess import check_call, CalledProcessError
from urllib import urlencode
import urllib
import json
import random
import base64
import tempfile
import shutil

HLS_PATH = '/data/vdp/vhls'
HLS_PROTECT_PATH = '/data/vdp/vprotecthls'
HDS_PATH = '/data/vdp/v720phds'

V360P_PATH = '/data/vdp/v360p'
V480P_PATH = '/data/vdp/v480p'
V720P_PATH = '/data/vdp/v720p'

SCRIPT_PATH = path.abspath(path.dirname(__file__))
sys.path += [SCRIPT_PATH]
if sys.platform.startswith('darwin'):
    BIN_PATH = path.join(SCRIPT_PATH, 'bin', 'macosx')
elif sys.platform.startswith('linux'):
    BIN_PATH = path.join(SCRIPT_PATH, 'bin', 'linux')
else:
    BIN_PATH = path.join(SCRIPT_PATH, 'bin', sys.platform)

print  BIN_PATH 

def curl(url,post):
    cmd = ['/usr/bin/curl','-s',
            '-d','"'+ post +'"',
            '"'+ url +'"']

    print "\ncurl:"
    print " ".join(cmd)
    cmd = " ".join(cmd)
    os.system(cmd)
    #try:
    #    check_call(cmd) 
    #except CalledProcessError, e:
    #   raise Exception("binary tool failed with error %d" % e.returncode)

def random_string(bytecount):
    return base64.b16encode(os.urandom(bytecount))

if not path.exists(BIN_PATH):
    raise Error("Platform not supported")

def mp4_ts(duration,in_mp4,out_ts):
    cmd = [path.join(BIN_PATH, 'mp42ts'),
           '--segment', str(duration),
            in_mp4,
            out_ts]

    print "\nmp42tsing media:"
    print " ".join(cmd)
    try:
        check_call(cmd) 
    except CalledProcessError, e:
        raise Exception("binary tool failed with error %d" % e.returncode)

def create_hls_playlist(out_path):
    cmd = ['/usr/local/bin/python2.7',
            path.join(SCRIPT_PATH, 'create-hls-playlist.py'),
            str(10),
            out_path]
    print "\ncreate-hls-playlisting media:"
    print " ".join(cmd)
    try:
        check_call(cmd) 
    except CalledProcessError, e:
        raise Exception("binary tool failed with error %d" % e.returncode)

def package_hls_files(out_path,vid,contentid,contentkey):
    try:
        os.makedirs(HLS_PROTECT_PATH+out_path)
    except:
        print 'protect path exists' 

    cmd = ['/usr/local/bin/python2.7',
            path.join(SCRIPT_PATH, 'package-hls-files.py'),
            '--key', contentkey,
            '--protection', 'bbts-2.0',
            '--output-dir',HLS_PROTECT_PATH+out_path,
            contentid,HLS_PATH+out_path+'/'+vid+'.m3u8']
    print "\npackage_hls_filesing media:"
    print " ".join(cmd)
    try:
        check_call(cmd) 
    except CalledProcessError, e:
        raise Exception("binary tool failed with error %d" % e.returncode)    

def package_hds_files(in_mp4,contentid,bitrate,out_path,manifest_file=None):

    tmpdir = tempfile.mkdtemp()
    tmpfile = path.join(tmpdir, contentid+'.mp4')
    shutil.copyfile(in_mp4, tmpfile)
    cmd=['/usr/local/f4fpackager/f4fpackager','--input-file='+tmpfile,'--content-id='+contentid,'--common-key=/usr/local/f4fpackager/m1905FlashAccess/m1905-license.key','--license-server-url=http://drmfa.m1905.com/flashaccessserver/sampletenant/','--license-server-cert=/usr/local/f4fpackager/m1905FlashAccess/m1905-license.der','--transport-cert=/usr/local/f4fpackager/m1905FlashAccess/m1905-transport.der','--packager-credential=/usr/local/f4fpackager/m1905FlashAccess/m1905-packager.pfx','--credential-pwd=1qazxsw2M1905packager','--fragment-duration=10','--policy-file=/usr/local/f4fpackager/m1905FlashAccess/ad-policy.pol','--bitrate='+str(bitrate),'--output-path='+out_path]

    if manifest_file:
        cmd += ['--manifest-file='+out_path+manifest_file]

    print "\npackage_hds_files media:"
    print " ".join(cmd)
    try:
        check_call(cmd) 
    except CalledProcessError, e:
        raise Exception("binary tool failed with error %d" % e.returncode)
    shutil.rmtree(tmpdir)

def get_outpath(vid):
    outpath = vid[0:1]
    if (outpath == 'm') :
        outpath = '/movie'
    else:
        outpath = '/video'
    outpath = outpath + '/' + vid[1:5] +'/' +  vid[5:7] +'/' +  vid[7:9]  +'/' + vid
    return outpath
def create_hls_ts(channelid,vid,videopath):
    outpath = get_outpath(vid)
    inpath = ''
    contentid = ''
    bitrate = ''
    manifest_file = ''
    channelid = int(channelid)
    if channelid == 7: 
        out_ts = outpath + '/'+vid+'-q300'
        inpath = V360P_PATH
        bitrate = '300'
        contentid = vid + '-300k'
    elif channelid == 8:
        out_ts = outpath + '/'+vid+'-q500'
        inpath = V480P_PATH
        bitrate = '500'
        manifest_file =vid + '-300k.f4m'
        contentid = vid + '-500k'
    elif channelid == 9:
        out_ts = outpath + '/'+vid+'-q800'
        inpath = V720P_PATH
        bitrate = '800'
        manifest_file =vid + '-500k.f4m'
        contentid =vid
    else:
        print 'channelid is error'
        sys.exit(1)

    try:
        os.makedirs(HLS_PATH+out_ts)
        os.makedirs(HDS_PATH+outpath)
    except:
        print 'path exists'
    package_hds_files(inpath+videopath,contentid,bitrate,HDS_PATH+outpath+'/',manifest_file)
    mp4_ts(10,inpath+videopath,HLS_PATH+out_ts+'/' + vid + '.%d.ts')
    return outpath

def main(args):
    usage = 'main.py <APIUrl>'
    #if len(args) != 1:
        #print usage
        #sys.exit(1)
    content = urllib.urlopen('http://192.168.97.146/api.php?op=video_api&action=last_video_list').read()
    jsondata = json.loads(content)

 
    if(isinstance(jsondata,dict)):
        for item in jsondata:
            tmp = jsondata[item]
            vid = item
            outpath = get_outpath(vid)
            hlspath = outpath+'/'+vid+'.m3u8'
            if(os.path.exists(HLS_PROTECT_PATH+hlspath)):
                print 'encoded'
                continue

            filmno=''
            vid=''
            for v in tmp:
                channelid = v['channelid']
                vid = v['vid']
                filmno = v['filmno']
                path = v['filepath']
                catid = v['catid']
                outpath = create_hls_ts(channelid,vid,path)
            contentid = 'cid:marlin#P1905:'+ filmno  +'@'+ random_string(16).lower()[0:8]
            contentkey = random_string(16)    
            print contentid

            url='http://192.168.97.146/api.php?op=video_api&action=add_video_info'
            if(os.path.exists(HDS_PATH+outpath+'/'+vid+'.f4m')):
                post = "vid="+vid+"&filmno="+filmno+"&videopath="+outpath+'/'+vid+'.f4m'+"&channelid=19";
                curl(url,post)

            create_hls_playlist(HLS_PATH+outpath)
            #if(os.path.exists(HLS_PATH+hlspath)):
                #post = "filmno="+filmno+"&videopath=" +hlspath+"&channelid=23";
                #curl(url,post)

            package_hls_files(outpath,vid,contentid,contentkey)
            if(os.path.exists(HLS_PROTECT_PATH+hlspath)):
                hlspath='{"path":"'+ hlspath +'", "contentid":"'+ contentid +'", "contentkey":"'+ contentkey +'"}'
                post = "vid="+vid+"&filmno="+filmno+"&videopath=" +urllib.quote(hlspath)+"&channelid=22";
                curl(url,post)
            sys.exit(1)
    else:
        print("no data")
                    
if __name__ == '__main__':
    main(sys.argv[1:])
