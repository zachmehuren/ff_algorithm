import pandas as pd
import os,sys
from astropy.table import Table,vstack
import numpy as np
from copy import deepcopy
from astropy.io import ascii
import os.path

cols={
    'P':'C:U',
    'D':'B:M'
}
headers={
    'D':5,
    'P':3
}

factors={
    'QB':{'comp':1.10,'yds':0.95,'td_int':0.85,'ttt':1.10,'oline':1.20},
    'TE':{'tar':1.20,'yds':1.00,'td_int':0.90,'sao':1.10,'oline':1.20},
    'RB':{'att':1.30,'yds':0.90,'td_int':0.90,'sao':1.10,'oline':1.20},
    'WR':{'tar':1.20,'yds':1.00,'td_int':0.90,'sao':1.10,'oline':1.20}
}

factors2={
    'QB':{'comp':1.10,'yds':0.95,'td_int':0.85,'ttt':1.10,'oline':1.20},
    'TE':{'tar':1.20,'yds':1.00,'td_int':0.90,'sao':1.10,'oline':1.20},
    'RB':{'att':1.30,'yds':0.90,'td_int':0.90,'sao':1.10,'oline':1.20},
    'WR':{'tar':1.20,'yds':1.00,'td_int':0.90,'sao':1.10,'oline':1.20}
}

pos=['QB','TE','RB','WR']

colname1={
    'QB':'comp',
    'TE':'tar',
    'RB':'att',
    'WR':'tar'
}

colname2={
    'QB':'ttt',
    'TE':'sao',
    'RB':'sao',
    'WR':'sao'
}

sheets=['P','D']

tables={}

path='ff_sheet.xlsx'

xls = pd.ExcelFile(path)
totals={}
rank_maxes=dict([])
rank_rels=dict([])

for x in pos:
    for s in sheets:
        a = xls.parse(x+'_'+s,header = headers[s], parse_cols = cols[s])
        if s=='P':
            tables[x+'_'+s]=Table()
            tables[x+'_'+s]['player']=a.iloc[:,0]
            tables[x+'_'+s]['player']=[y.lower() for y in tables[x+'_'+s]['player']]
            tables[x+'_'+s]['p_yds']=a.iloc[:,1]
            tables[x+'_'+s]['p_td']=a.iloc[:,2]
            tables[x+'_'+s]['p_int']=a.iloc[:,3]
            tables[x+'_'+s]['ru_rush']=a.iloc[:,5]
            tables[x+'_'+s]['ru_yds']=a.iloc[:,6]
            tables[x+'_'+s]['ru_td']=a.iloc[:,7]
            tables[x+'_'+s]['r_rec']=a.iloc[:,9]
            tables[x+'_'+s]['r_yds']=a.iloc[:,10]
            tables[x+'_'+s]['r_td']=a.iloc[:,11]
            tables[x+'_'+s]['r_tar']=a.iloc[:,12]
            tables[x+'_'+s]['m_2pc']=a.iloc[:,14]
            tables[x+'_'+s]['m_fuml']=a.iloc[:,15]
            tables[x+'_'+s]['m_td']=a.iloc[:,16]
            tables[x+'_'+s]['m_pts']=a.iloc[:,18]
        else:
            totals[x+'_'+s]=Table()
            tables[x+'_'+s]=Table()
            tables[x+'_'+s]['age']=a.iloc[:,0]
            tables[x+'_'+s]['player']=a.iloc[:,2]
            tables[x+'_'+s]['player']=[y.lower() for y in tables[x+'_'+s]['player']]
            tables[x+'_'+s][colname1[x]]=a.iloc[:,3]/factors[x][colname1[x]]
            tables[x+'_'+s]['yds']=a.iloc[:,5]/factors[x]['yds']
            tables[x+'_'+s]['td_int']=a.iloc[:,7]/factors[x]['td_int']
            tables[x+'_'+s][colname2[x]]=a.iloc[:,9]/factors[x][colname2[x]]
            tables[x+'_'+s]['oline']=a.iloc[:,11]/factors[x]['oline']

            tables[x+'_'+s][colname1[x]]*=factors2[x][colname1[x]]
            tables[x+'_'+s]['yds']*=factors2[x]['yds']
            tables[x+'_'+s]['td_int']*=factors2[x]['td_int']
            tables[x+'_'+s][colname2[x]]*=factors2[x][colname2[x]]
            tables[x+'_'+s]['oline']*=factors2[x]['oline']

            totals[x+'_'+s][x]=tables[x+'_'+s][colname1[x]]+tables[x+'_'+s]['yds']+tables[x+'_'+s]['td_int']+tables[x+'_'+s][colname2[x]]+tables[x+'_'+s]['oline']
            rank_maxes[x]=np.max(totals[x+'_'+s][x])
            tables[x+'_'+s]['rels']=totals[x+'_'+s][x]/rank_maxes[x]
            tables[x+'_'+s].sort('rels')

remove=[]
ppg={
    'QB':{},
    'TE':{},
    'WR':{},
    'RB':{}
}

for pos in ppg.keys():
    common=[x for x in tables[pos+'_P']['player'] if x in tables[pos+'_D']['player']]
    remove=[]
    for row in range(len(tables[pos+'_P'])):
        if tables[pos+'_P']['player'][row] not in common:
            remove.append(row)
    tables[pos+'_P'].remove_rows(remove)
    remove=[]
    for row in range(len(tables[pos+'_D'])):
        if tables[pos+'_D']['player'][row] not in common:
            remove.append(row)
    tables[pos+'_D'].remove_rows(remove)

first,last,pos,pts=np.loadtxt('ffpg.csv',dtype='str',unpack=True,delimiter=',')

for p in ppg.keys():
    temp_first=[first[i] for i in range(len(first)) if pos[i]==p]
    temp_last=[last[i] for i in range(len(first)) if pos[i]==p]
    temp_pts=[pts[i] for i in range(len(first)) if pos[i]==p]
    ppg[p]={temp_first[i].lower()+' '+temp_last[i].lower():temp_pts[i] for i in range(len(temp_first))}
    tables[p+'_P'].sort('m_pts')
pts_rel={}
pts_maxes={}
remove=[]
remove2=[]
max_pts=0
for p in ppg:
    for player in ppg[p]:
        if float(ppg[p][player])>max_pts:
            max_pts=float(ppg[p][player])
for table in tables:
    if table[-1]=='P':
        for i in range(len(tables[table])):
            if tables[table]['player'][i] in ppg[table[0:2]].keys():
                tables[table]['m_pts'][i]=ppg[table[0:2]][tables[table]['player'][i]]
            else:
                remove.append(i)
                for j in range(len(tables[table[0:2]+'_D'])):
                    if tables[table[0:2]+'_D']['player'][j]==tables[table]['player'][i]:
                        remove2.append(j)
                        break
        tables[table].remove_rows(remove)
        tables[table[0:2]+'_D'].remove_rows(remove2)
        tables[table]['m_pts']=tables[table]['m_pts']/max_pts#np.max(tables[table]['m_pts'])
        #print(tables[table])
    remove=[]
    remove2=[]

fpts=1
ranks=0
current_mean={
    'QB':{},
    'TE':{},
    'WR':{},
    'RB':{}
}

net={
    'QB':{},
    'TE':{},
    'WR':{},
    'RB':{}
}
current_std={
    'QB':{},
    'TE':{},
    'WR':{},
    'RB':{}
}
global pick_data
pick_data={}

for pos in current_std.keys():
    if os.path.isfile('current_'+pos+'.dat'):
        pick_data[pos]=ascii.read('current_'+pos+'.dat')
        round_number,pick=np.loadtxt('round.dat',unpack=True)
    else:
        pick_data[pos]=Table([tables[pos+'_P']['player'],tables[pos+'_P']['m_pts'].astype(float),tables[pos+'_D']['rels'].astype(float)])
        round_number=0
        pick=1


def runAlg():
    print('Top picks by position:')
    temp_table=None
    pick_table=deepcopy(pick_data)
    print(pick_data['QB'])
    top_picks={}
    for pos in pick_data.keys():
        print(pos)
        print(fpts)
        pick_table[pos]['net']=fpts*pick_data[pos]['m_pts']+ranks*pick_data[pos]['rels']


        pick_table[pos].remove_column('m_pts')
        pick_table[pos].remove_column('rels')
        pick_table[pos].sort('net')
        pick_table[pos].reverse()

        for row in range(len(pick_table)):
            print(pick_table[pos][row])

        current_mean[pos]=np.mean(pick_table[pos]['net'][0:24])
        current_std[pos]=np.std(pick_table[pos]['net'][0:24])
        #max=np.max((pick_table[pos]['net']-current_mean[pos])/current_std[pos])
        pick_table[pos]['res']=(pick_table[pos]['net']-current_mean[pos])/current_std[pos]

        pick_table[pos].sort('res')
        pick_table[pos].reverse()
        pick_table[pos].remove_column('net')
        top_picks[pos]=np.array(pick_table[pos][0:3])
        for i in range(3):
            print('%i. %s=%f'%(i+1,top_picks[pos][i][0],top_picks[pos][i][1]))
        pick_table[pos]['pos']=pos
        if temp_table:
            temp_table=vstack([temp_table,pick_table[pos]])
        else:
            temp_table=pick_table[pos]
        temp_table.sort('res')
        temp_table.reverse()
        print('Top current picks:')
    for i in range(10):
        print('%i. %s-%s (%f)'%(i+1,temp_table['pos'][i],temp_table['player'][i],temp_table['res'][i]))


my_picks=[11,14,35,38,59,62,83,86,107,110,131,134,155,158,179,182,203,206,227,230,251,254,275,278,299]
#new_round=[1,13,25,37,49,72,73,96,97,120,121,144,145,168,169,192,193,216,217,240,241,264,265,288,289]
new_round=[1+12*i for i in range(25)]

my_team={
    'QB':[],
    'RB':[],
    'WR':[],
    'TE':[]
}

while(round_number<=25):
    if pick in new_round:
        if fpts>=0:
            fpts=1-.1*round_number
        ranks=1-fpts
        round_number+=1
        print('')
        print('____________________________________________________')
        print('Round %i:'%round_number)
        if np.max([len(my_team[x]) for x in my_team.keys()]) > 0:
            print('')
            print('Your team:')
            for pos in my_team:
                print(pos+':  ,'.join(my_team[pos]))

    runAlg()

    person=True
    print('Current pick:%i'%pick)
    while person:
        print('')
        picked=raw_input('Player picked: ')
        for pos in ppg.keys():
            if picked in pick_data[pos]['player']:
                if pick in my_picks:
                    my_team[pos].append(picked)

                pick_data[pos].remove_row(np.where(pick_data[pos]['player']==picked)[0][0])
                person=False
                break
        if person:
            print('That player is not in the list, try again.')
        else:
            break
    pick+=1
    for pos in pick_data.keys():
        ascii.write(pick_data[pos],'current_'+pos+'.dat',overwrite=True)
    np.savetxt('round.dat',[round_number,pick])
