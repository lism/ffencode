#!/bin/bash
id="hduser"
outpath=/data/hadoop/tmp/$(date +%s%N)
type="v360p"
dt=$(date +%Y/%m/%d)
mkdir -p $outpath/$type
host=`hostname`
pwd=`pwd`
uid=`whoami`
put_dir=/data/vdp/$type/
dt=""
cd "$outpath"
true > a
while read line; do
input=`echo $line | awk '{ print $1 }'`
filename=`basename $input .mp4`

if [ "$dt" == "" ]; then
	tmpfilename=${filename%.*}
	if [ "${tmpfilename:0:1}" == "m" ]; then
	        dt="movie"
	else
	        dt="video"
	fi
	dt="${dt}/${tmpfilename:1:4}/${tmpfilename:5:2}/${tmpfilename:7:2}/${tmpfilename}/"
fi
base=$put_dir$dt

encodeinfo="movie=/usr/hadoop/newlogo.png,scale=96:-1[watermark];movie=/usr/hadoop/pindaologo50px.png,scale=22:-1[watermark2];[in]scale=480:trunc(ow/a/2)*2[scale];[scale][watermark]overlay=10:10[1];[1][watermark2]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]"
encodep=`echo $line | awk '{ print $2 }'`
encodebit=`echo $line | awk '{ print $3 }'`
encodex=`echo $line | awk '{ print $4 }'`
encodetit=`echo $line | awk '{ print $5 }'`
encodecrop=`echo $line | awk '{ print $6 }'`
autocrop=""
if [ "$encodecrop" != "" ]; then
        autocrop=${encodecrop},
fi
if [ "$encodex" == "0" ]; then
    autocrop=""
fi
case $encodep in
0)
    encodeinfo="${autocrop}scale=480:trunc(ow/a/2)*2"
    ;;
1)
    encodeinfo="movie=/usr/hadoop/newlogo.png,scale=70:-1[watermark];[in]${autocrop}scale=480:trunc(ow/a/2)*2[scale];[scale][watermark]overlay=10:10[out]"
    ;;
2)  
    encodeinfo="movie=/usr/hadoop/newlogo.png,scale=70:-1[watermark];movie=/usr/hadoop/pindaologo50px.png,scale=22:-1[watermark2];[in]${autocrop}scale=480:trunc(ow/a/2)*2[scale];[scale][watermark]overlay=10:10[1];[1][watermark2]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]"
    ;;
3)  
    encodeinfo="movie=/usr/hadoop/1905wow.png,scale=70:-1[watermark];movie=/usr/hadoop/pindaologo50px.png,scale=22:-1[watermark2];[in]${autocrop}scale=480:trunc(ow/a/2)*2[scale];[scale][watermark]overlay=10:10[1];[1][watermark2]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]"
    ;;
4)
    encodeinfo="movie=/usr/hadoop/1905wow.png,scale=70:-1[watermark];[in]${autocrop}scale=480:trunc(ow/a/2)*2[scale];[scale][watermark]overlay=10:10[out]"
    ;;
esac

/usr/hadoop/bin/hadoop fs -get $input $outpath 2>&1
ffmpeg -y -i $outpath/$filename.mp4 -threads 6 -vcodec libx264 -pix_fmt yuv420p -vprofile baseline -preset slow  -keyint_min 25 -g 25 -b:v 300k -maxrate 300k -bufsize 600k -vf "${encodeinfo}" -acodec libfdk_aac -ac 2 -b:a 32k -af 'volume=1.5' $outpath/$type/$filename.qt.mp4 < a 2>&1
/usr/bin/qt-faststart $outpath/$type/$filename.qt.mp4 $outpath/$type/$filename.mp4 < a 2>&1
/usr/hadoop/bin/hadoop fs -put  $outpath/$type/$filename.mp4 ${base}/$filename.mp4 2>&1
/usr/hadoop/bin/hadoop fs -chown $id ${base}/$filename.mp4 2>&1
done
rm -f a
rm -rf $outpath

