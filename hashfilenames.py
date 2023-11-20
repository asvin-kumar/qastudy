import os
from os.path import join
import hashlib
import shutil
from tqdm import tqdm
from glob import glob
import pandas as pd
import numpy as np

def getvidlist():
    vidlistpath = "vidlist.txt"
    vidlist = open(vidlistpath, 'r').read().strip().splitlines()
    vids = [x.split(' ')[0].split('/')[-1] for x in vidlist]
    return vids

def construct_names_map():

    # networks = ['basicvsrpp', 'rrn']
    # models = ['base', 'p05', 'p075', 'p09', 'p095', 'p096']
    
    networks = ['basicvsrpp', 'vrt', 'rrn']
    models = ['base', 'p05', 'p075', 'p09', 'p095', 'p096', 'p0965', 'p097', 'p098', 'p099']
    vids = getvidlist()

    allvids = [x+'_'+y+'_'+z for x in vids for y in networks for z in models]
    gtlist = [x+'_gt' for x in vids]
    allvids.extend(gtlist)

    allhash = []
    alllines = []
    vidmap = {}

    for i, f in enumerate(allvids):
        h = hashlib.sha256()
        h.update(f.encode('utf-8'))
        hs = h.hexdigest()
        allhash.append(hs)

        vidmap[f] = hs[:16]

        line = ' '.join([hs[:16], f]) + '\n'
        alllines.append(line)

    with open('map.txt', 'w') as outfile:
        outfile.writelines(alllines)

    valid = len(set(allhash)) == len(allhash)
    return vidmap, valid

def get_video_times(TIME_FILE):
    with open(TIME_FILE, 'r') as f:
        times = f.read().strip().splitlines()
    timedict = {}
    for t in times:
        parts = t.split(' ')
        timedict[parts[1]+'.mp4'] = parts[0]
    return timedict

def rename_files(oldfolder, newfolder, vidmap):

    timedict = get_video_times('vidduration.txt')

    vidlist = glob(join(oldfolder, '*.mp4'))
    # print(vidlist[:10])
    # assert len(vidlist) == 744

    os.makedirs(newfolder, exist_ok=True)

    newtimes = []
    for v in tqdm(vidlist):
        v1 = v.split(os.sep)
        v2 = v1[-1].split('.')
        v3 = v2[0]
        # print(v)
        if v3 in vidmap:
            oldname = join(oldfolder, v3+'.'+v2[-1])
            newname = join(newfolder, vidmap[v3]+'.'+v2[-1])
            shutil.move(oldname, newname)
        else:
            print(f'[*] Key {v3} not found in vidmap')
        
        if 'gt' not in v3:
            sc = '_'.join(v3.split('_')[:-2]) + '.mp4'
        else:
            sc = '_'.join(v3.split('_')[:-1]) + '.mp4'
        newtimes.append(f"{timedict[sc]} {vidmap[v3]}.mp4\n")
    
    with open('viddurationhash.txt', 'w') as f:
        f.writelines(newtimes)

def undo_rename():
    return

def update_csv(csvin, csvout, vidmap):
    # Step 1 - Read CSV
    df = pd.read_csv(csvin, header=None)

    # Step 2 - Rename
    new0 = []
    for i in range(len(df[0])):
        sessionlist = list(eval(df[0][i]))
        tmp = []
        for j in sessionlist:
            k = j.split('.')[0]
            tmp.append(vidmap[k]+'.mp4')
        new0.append(tmp)
    
    new1 = []
    for i in range(len(df[0])):
        sessionlist = list(eval(df[0][i]))
        tmp = []
        for j in sessionlist:
            k = j.split('.')[0]
            tmp.append(vidmap[k])
        new1.append(tmp)

    # Step 3 - Write to CSV
    d = {'session1': new0, 'session2': new1, 'email': " "}
    dfnew = pd.DataFrame(data=d)
    dfnew.to_csv(csvout, index=False, header=False)

if __name__ == '__main__':

    # TODO
    # This script needs to do these things:
    # 1. Create a hash map
    # 2. Rename files (because copying videos is too expensive)
    # 3. Provide option to undo the rename
    # 4. Create new csv file
    # 5. Create new vid duration file

    vidmap, valid = construct_names_map()
    while valid is False:
        vidmap, valid = construct_names_map()

    basefolder = '/Volumes/asvinhdd/PruningStudy/code/vqa_program'
    csvin = join(basefolder, 'videolist.csv')
    csvout = join(basefolder, 'newvideolist.csv')
    update_csv(csvin, csvout, vidmap)

    basefolder = '/Volumes/asvinhdd/PruningStudy/videos'
    oldfolder = join(basefolder, "output_videos_bk2")
    newfolder = join(basefolder, "output_videos_bk2_1117")
    rename_files(oldfolder, newfolder, vidmap)