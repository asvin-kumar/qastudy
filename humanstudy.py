# -*- coding: utf-8 -*-
from psychopy import visual, core, event, gui, logging
import os, time
import pandas as pd
from os.path import join, exists
from datetime import datetime
import time
import platform
import subprocess

# # define some global variables
# BASE                = 'E:\\PruningStudy\\'
# SCORE_DIR           = BASE + 'score'
# VIDEO_DIR           = BASE + 'videos\\output_videos'
# SESSIONLIST_FILE    = BASE + 'code\\videolisthash.csv'
# TIME_FILE           = BASE + 'times\\viddurationhash.txt'
# TIME_DIR            = BASE + 'times'
# # VIDPLAYER         = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
# VIDPLAYER           = "C:\\Program Files\\DAUM\\PotPlayer\\PotPlayerMini64.exe"
# SCREEN_SIZE         = (3840,2160)

BASE = '/Users/akv684/Library/CloudStorage/GoogleDrive-asvin@utexas.edu/My Drive/ASL/'
SCORE_DIR = BASE + 'scores/'
VIDEO_DIR = BASE + 'vids'
SESSIONLIST_FILE  = 'videolist.csv'
TIME_DIR = BASE + 'times'
TIME_FILE = BASE + 'vidduration.txt'
EMAIL_FILE = BASE + 'emails.txt'
SCREEN_SIZE = (3840,2160)
VIDPLAYER = "/Applications/VLC.app/Contents/MacOS/VLC"

#################################
# Functions to read data
#################################

def get_video_times():
    with open(TIME_FILE, 'r') as f:
        times = f.read().strip().splitlines()
    timedict = {}
    for t in times:
        parts = t.split(' ')
        timedict[parts[1]] = int(parts[0])
    timedict['turtles.mp4'] = 8
    return timedict

def read_email_file():
    if exists(EMAIL_FILE):
        with open(EMAIL_FILE, 'r') as f:
            emails = f.read().strip().splitlines()
    else:
        emails = []
    emaildict = {}
    maxid = 0
    for e in emails:
        parts = e.split('\t')
        emaildict[parts[1]] = int(parts[0])
        maxid = max(maxid, int(parts[0]))
    # emaildict['a@a.a'] = 33
    return emaildict, maxid

def update_email_file(sid, email):
    if exists(EMAIL_FILE):
        with open(EMAIL_FILE, 'a') as f:
            f.write(f"{sid}\t{email}\n")
    else:
        with open(EMAIL_FILE, 'w') as f:
            f.write(f"{sid}\t{email}\n")
    return

def get_video_list(sid, session):
    # read the video list for the session
    df_list = pd.read_csv(SESSIONLIST_FILE, header=None)
    video_list = list(eval(df_list[int(session)-1][int(sid)-1]))
    video_list = ['turtles']
    return video_list

#################################
# Functions for output screens during sessions
#################################

def show_text(text):

    # Window full or not
    win = visual.Window(size=SCREEN_SIZE, fullscr=True)            
                        
    #win.recordFrameIntervals = True
    #logging.console.setLevel(logging.WARNING)

    txt = visual.TextStim(win, text=text, font='Arial', pos=(0, 0), height=0.05, wrapWidth=1.5, ori=0,
                            color='black', colorSpace='rgb', opacity=1, depth=0)
    txt.draw()
    win.flip()
    core.wait(0)
    event.waitKeys(keyList = ['return'])
    win.mouseVisible = False
    win.close()
    return

def train():
    video_dir = BASE + 'sample_videos\\'
    video_list = ['01_basicvsrpp_base.mp4','08_rrn_p075.mp4']
    
    for video in video_list:

        if 'vlc' in VIDPLAYER or 'VLC' in VIDPLAYER:
            # Add IF for macOS and Windows
            cmd = f"\"{VIDPLAYER}\" --fullscreen --no-qt-fs-controller --no-video-title-show --no-keyboard-events --no-embedded-video --no-mouse-events --mouse-hide-timeout=0 {video_dir + video} vlc://quit"
        elif 'PotPlayer' in VIDPLAYER:
            cmd = f"\"{VIDPLAYER}\"  {join(video_dir, video)}"
        else:
            raise "Unknown Video Player"
        
        print(cmd)
        os.system(cmd)
        
        win = visual.Window(size=SCREEN_SIZE, fullscr=True)  
        win.mouseVisible = True

        rating = visual.RatingScale(win=win, name='rating', precision='100', marker='triangle', 
                            textColor='black', textSize=0.8, markerColor='DarkRed', showValue=False, mouseOnly=True, 
                            tickHeight=0, size=1.0, pos=[0, 0], low=1, high=100, labels=['Bad',' Excellent'], 
                            scale='Please provide a video quality score.')
        text = visual.TextStim(win, text='Poor           Fair           Good',
                             pos=(-0.003, -0.07), height=0.05, wrapWidth=1.5, ori=0,
                             color='black', colorSpace='rgb', opacity=1,
                             depth=0)

        while rating.noResponse:
            rating.draw()
            text.draw()
            win.flip()
        
        print('rating:',rating.getRating())

        rating.reset()
        win.close()

def study(video_list, sid, session_scorefile):
    
    text = 'Study begins! Press Enter!\nThis study will be about 45 minutes long.'
    show_text(text)

    df_score = None
    timedict = get_video_times()

    for index, video in enumerate(video_list):

        video = video+'.mp4' # forgot to do this when updating CSV to hashed file names

        if 'vlc' in VIDPLAYER or 'VLC' in VIDPLAYER:
            if 'macOS' in platform.platform():
                # Go to VLC -> Settings -> Show All -> Interface -> Main Interfaces -> macosx -> Behavior -> Uncheck "Show fullscreen controller"
                cmd = f"{VIDPLAYER} --quiet --fullscreen --no-embedded-video --video-on-top --no-video-title-show --no-keyboard-events --no-mouse-events --mouse-hide-timeout=0 \"{join(VIDEO_DIR, video)}\" vlc://quit"
            elif 'window' in platform.platform():
                cmd = f"\"{VIDPLAYER}\" --fullscreen --no-qt-fs-controller --no-video-title-show --no-keyboard-events --no-embedded-video --no-mouse-events --mouse-hide-timeout=0 {join(VIDEO_DIR,video)} vlc://quit"
            else:
                raise "Unknown platform."
        elif 'PotPlayer' in VIDPLAYER:
            cmd = f"\"{VIDPLAYER}\"  {join(VIDEO_DIR, video)}"
        else:
            raise "Unknown Video Player"
        # print(cmd)
        
        # time this command to catch cheaters who close the video player
        start = time.time()
        # os.system(cmd)
        subprocess.call(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
        end = time.time()

        obs_time = end-start
        key = '_'.join(video.split('_')[:-2])
        key = video
        exp_time = timedict[key]

        if(obs_time < exp_time):
            disp_string = f'The video player was closed earlier than expected. This incident will be investigated.\nPlease provide a video quality score.\nYou have completed {index+1} videos out of {len(video_list)}.\n'
            with open(join(TIME_DIR,f'{sid}.txt'), 'a') as fout:
                fout.write(f'Subject {sid} took {obs_time}s of {exp_time}s expected for video {video} played on {datetime.now().strftime("%m/%d/%Y at %H:%M:%S")}\n')
        else:
            vidword = 'video'+('s' if index else '')
            disp_string = f'You have completed {index+1} {vidword} out of {len(video_list)}.'

        win = visual.Window(size=SCREEN_SIZE, fullscr=True)  
        win.mouseVisible = True

        progress = visual.TextStim(win, text = disp_string,
                             pos=(0.0, 0.7), height=0.06, wrapWidth=1.5, ori=0,
                             color='black', colorSpace='rgb', opacity=1,
                             depth=0)

        rating = visual.RatingScale(win=win, name='rating', precision='100', marker='triangle', 
                                textColor='black', textSize=0.8, markerColor='DarkRed', showValue=False, mouseOnly=True, 
                                tickHeight=0, size=1.0, pos=[0, 0], low=1, high=100, labels=['Bad', ' Excellent'], 
                                scale='Please provide a video quality score.')
        
        text = visual.TextStim(win, text='Poor           Fair           Good',
                             pos=(-0.003, -0.07), height=0.05, wrapWidth=1.5, ori=0,
                             color='black', colorSpace='rgb', opacity=1,
                             depth=0)
        
        while rating.noResponse:
            progress.draw()
            rating.draw()
            text.draw()
            win.flip()

        # print('rating:',rating.getRating())
        score = rating.getRating()

        df_score = pd.concat([df_score, pd.DataFrame([video,score]).transpose()])
        # df_score.reset_index(drop=True)
        df_score.to_csv(join(SCORE_DIR, session_scorefile))
        
        rating.reset()
        win.close()

    text = 'Study ends!\n Thanks very much for your participation!'
    show_text(text)

    return

#################################
# Functions for output screens during sessions
#################################

def display_errors(text, sid=None):
    msgDlg = gui.Dlg(title='Start study')
    msgDlg.addText(text)
    if sid is not None:
        msgDlg.addText(f"ID: {sid}")
    msgDlg.show()
    core.quit()

def get_email_session():

    # Open id and session selection interface
    info = {'Email':'', 'Session':''}
    infoDlg = gui.DlgFromDict(dictionary=info, title='Start study', order=['Email','Session'])
    
    if infoDlg.OK == False:
        core.quit()
        
    email = info['Email']
    session = info['Session']

    if email == "":
        display_errors('Subject did not enter email, exiting.')

    if session == "":
        display_errors('Subject did not enter session #, exiting.')

    return email, session

def validate_email_session(email, session):

    emaildict, maxid = read_email_file()

    if session == "1":
        if email in emaildict:
            sid = emaildict[email]
        else:
            sid = maxid+1
            update_email_file(sid, email)
    elif session == "2":
        if email in emaildict:
            sid = emaildict[email]
            session_scorefile  = f'score_{sid}_{1}.csv'
            if not exists(join(SCORE_DIR, session_scorefile)):
                display_errors("Please complete session 1 first.")
        else:
            display_errors("Please complete session 1 first.")
    else:
        display_errors(f"Invalid session value.")
    
    session_scorefile  = f'score_{sid}_{session}.csv'
    if exists(join(SCORE_DIR, session_scorefile)):
        display_errors(f"File for {email} and session {session} already exists.", sid)

    return sid, session_scorefile

def runinterface():

    email, session = get_email_session()

    sid, session_scorefile = validate_email_session(email, session)

    video_list = get_video_list(sid, session)
    # print(len(video_list))

    if session == "1":
        text = 'Thank you for your participation!\n\n\
    You will be watching a set of videos one after the other.\n\n\
    At the end of each video, a rating screen will be presented to you.\n\n\
    For each video, please provide an overall quality score by choosing on the continuous rating bar.\n\n\
    If you have any questions please ask them now.\n\n\
    Hit Enter to start the training!'
        show_text(text)
        # train()
        study(video_list, sid, session_scorefile)
    elif session == "2":
        text = 'Thank you for your participation!\n\n\
        You will be watching a set of videos one after the other.\n\n\
        At the end of each video, a rating screen will be presented to you.\n\n\
        For each video, please provide an overall quality score by choosing on the continuous rating bar.\n\n\
        If you have any questions please ask them now.\n\n\
        Since this is the second session, there will be no training.\n\n\
        Hit Enter to start the testing!'
        show_text(text)
        study(video_list, sid, session_scorefile)

    core.quit()

if __name__ == '__main__':
    runinterface()