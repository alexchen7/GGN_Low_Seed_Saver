# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 20:27:29 2020

@author: Achan
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import os.path
import os

# change the current directory to file directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def GGN_auto_snatch():
    
    """auto search low seeded torrents and download to designated folders,
    build a csv file to record the time of download. SO FAR, ONLY 
    URL recording was accomplished"""
    
    page_num = 0
    
    # desired total size (GB)
    desired_size = 1024
    
    # initialze total size
    total_size = 0
    
    # total torrents
    total_torrent= 0
    
    while page_num <= 15 and total_size < desired_size:
        
        #START WITH GENERAL PARAMETERS
        
        page_num += 1
        page_num = str(page_num)
        
        url = "https://gazellegames.net/torrents.php?page=" + page_num + "&order_way=desc&order_by=size&action=advanced"
        
        cookies = {}
        
        torrent_page_r = requests.get(url, cookies = cookies)
        
        torrent_page = BeautifulSoup(torrent_page_r.text, features = 'lxml')
        
        # re for torrent line
        torrent_line_reg = re.compile(".+groupid_.+ edition_.+")
        
        # time format of uploaded time
        time_reg = re.compile("[JFMASOND][a-z][a-z] \d{2} \d{4}, \d{2}:\d{2}")
        
        # torrent link reg
        torrent_link_reg = re.compile("torrents\.php.*torrent_pass=\w{32}")
        
        # torrent id reg
        torrent_id_reg = re.compile("torrents.php.*torrentid=\d*")
        
        # size conversion to Bytes
        size_conversion = {'B': 1, 'KB':1024, 'MB': 1024**2, 'GB':1024**3, \
                           'TB':1024**4}
        
        # keyword of promotions
        promotions = {'Free Leech!':'FL', 'Neutral Leech!':'NL'}
        
        # torrent status
        statuses = {'color_seeding': 'seeding', 'color_snatched':'snatched', \
                    'color_leeching': 'leeching'}
        
        # file name
        file_name = 'low_seed.txt'
        # GENERAL PARAMETERS END
        
        # find the torrent section
        torrent_section = torrent_page.find_all('table', attrs = {'class': \
        'torrent_table grouping', 'id': 'torrent_table'})
        
        # get the torrent section from the result set
        torrent_section = torrent_section[0]
        
        # get the torrent lines
        torrent_lines = torrent_section.findAll('tr', attrs = {'class': torrent_line_reg})
        
        
        count = 0

        for line in torrent_lines:
            # BEGIN TORRENT INFO COLLECTION
            
            # slice every piece of info into iteratable form
            torrent_info = line.findAll('td')
            
            # uploaded time piece
            uploaded_time_chunk = str(torrent_info[1])
            
            # get upload time
            uploaded_time_position = re.search(time_reg, uploaded_time_chunk)
            uploaded_time_position = uploaded_time_position.span()
            uploaded_time = uploaded_time_chunk[uploaded_time_position[0]: \
                                                uploaded_time_position[1]]
            
            uploaded_time = datetime.strptime(uploaded_time, '%b %d %Y, %H:%M')
            
            # calculate the uptime, plus 1 day to prevent possible timezone err
            today = datetime.today() + timedelta(days=1)
            
            up_time = today - uploaded_time
            
            # url of the torrent, use if to exclude external link torrents
            if torrent_info[0].span.a.text == 'DL':
                torrent_link_chunck = str(torrent_info[0].span.a)
                torrent_link = re.findall(torrent_link_reg, torrent_link_chunck)
                
                # cleanup "&amp;" and domain name of GGN
                torrent_link = "http://gazellegames.net/" + \
                torrent_link[0].replace("&amp;", "&")
            # incase it's external link   
            else:
                continue
            
            # num of seeders and leechers
            try:
                seeder = int(torrent_info[5].text)
                leecher = int(torrent_info[6].text)
            except:
                seeder = 0
                leecher = 0
            
            # name of the torrent
            name = torrent_info[0].findAll('a')[2].text
            if name=='RP':
                name = torrent_info[0].findAll('a')[3].text
            
            # info link of the torrent
            info_link = re.findall(torrent_id_reg, str(torrent_info[0]))
            info_link = "http://gazellegames.net/" + \
            info_link[0].replace('&amp;', '')

                
            # size of the torrent
            size = torrent_info[3].text.split()
            size = float(size[0].replace(',','')) * size_conversion[size[1]]
            
            # seed promotion
            for i in promotions:
                if i in str(torrent_info[0]):
                    promotion = promotions[i]
                    break
                promotion = 'no'
            
            # trumpable or not
            if 'Trumpable' in str(torrent_info[0]):
                trumpable = True
            else:
                trumpable = False
            
            # seed status
            for i in statuses:
                if i in str(torrent_info[0]):
                    status = statuses[i]
                    break
                status = 'not snatched'
                
            #FINISHED TORRENT INFO COLLECTION
            
            
            #BEGIN TORRENT SELECTION PART
            
            # start with less than 4 seeders
            if (seeder + leecher) < 4 and seeder != 0 and up_time > timedelta(days=365) and status!='NL':
                # filter out trumpable
                if not trumpable:
                    # filter existed torrents
                    if status != 'seeding' and status!= 'leeching' and status!= 'snatched':
                        # download
                        f = open(file_name, "a")
                        f.write(torrent_link + '\n')
                        f.close()
                        print (name, '\n', info_link, '\n', '{}GB'.format(round(size/1024**3,3)), '{}days'.format(up_time.days), '{}peers'.format(seeder), '{}leechers'.format(leecher), 'promotion:{}'.format(promotion), 'status:{}'.format(status), '\n\n')
                        total_size += size/1024**3
                        total_torrent += 1
                                                
            elif (seeder + leecher) == 4 and seeder != 0 and up_time > timedelta(days = 365*3) and status!='NL':
                if not trumpable:
                    # filter existed torrents
                    if status != 'seeding' and status!= 'leeching' and status!= 'snatched':
                        # download
                        f = open(file_name, "a")
                        f.write(torrent_link + '\n')
                        f.close()
                        print (name, '\n', info_link, '\n', '{}GB'.format(round(size/1024**3,3)), '{}days'.format(up_time.days), '{}peers'.format(seeder), '{}leechers'.format(leecher), 'promotion:{}'.format(promotion), 'status:{}'.format(status), '\n\n')
                        # doing stats
                        total_size += size/1024**3
                        total_torrent += 1
            
        page_num = int(page_num)
		
		# don't crash the server
        time.sleep(5)
    
    f = open(file_name, "a")
    summary = 'We have gone to page {}! {} of low torrents were mined with total size of {} GB!'.format(page_num, total_torrent, total_size)
    print (summary)
    f.write(summary)
    f.close()
    
    return count

