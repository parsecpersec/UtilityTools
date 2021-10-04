from pandas import read_excel, isnull
import os, time, sys, shutil
info = read_excel(r"D:\photos2folders\information.xlsx")
FROM = r'D:\DCIM'

def find_dir(path):
    filelist = []
    for root, dirs, files in os.walk(path):
        for name in files:
            filelist.append(os.path.join(root, name))
    new = os.path.getctime(filelist[0])
    newest_file = filelist[0]
    for img_file in filelist:
        t = os.path.getctime(img_file)
        if t > new:
            new = t
            newest_file = img_file
    date = str(time.strftime('%Y%m%d', time.localtime(new)))
    dir_name = os.path.dirname(os.path.abspath(newest_file))
    return date, dir_name

DATE, DirName = find_dir(FROM)
TO = r'D:\ZX' + DATE + '\\'
FROM_WHERE = DirName + '\\'

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_name(data):
    for i in range(0, len(data)):
        if isnull(data.iloc[i, 2]):
            data.loc[i, 'Dir_Name'] = str(data.iloc[i, 1]) + ' ' + data.iloc[i, 0] + ' ' + data.iloc[i, 3]
        else:
            data.loc[i, 'Dir_Name'] = str(data.iloc[i, 1]) + r'（old）' + data.iloc[i, 0] + ' ' + data.iloc[i, 3]

def find_file(data):
    split = []
    finished = []
    sep = '、'
    for i in range(0, len(data)):
        split.append(data.loc[i, 'File'].split(sep))
    for i in range(0, len(split)):
        complete = []
        for j in range(0, len(split[i])):
            if '-' in split[i][j]:
                edge = split[i][j].split('-')
                edge[0] = int(edge[0])
                edge[1] = int(edge[1])
                for k in range(edge[0], edge[1] + 1):
                    complete.append(k)
            else:
                complete.append(int(split[i][j]))
        complete.sort()
        finished.append(complete)
    return finished

def copy(path, data, files):
    for i in range(0, len(files)):
        if i != 0:
            print('')
        screen = sys.stdout
        folder = data.iloc[i, 5]
        n_exist = 0
        for j in range(0, len(files[i])):
            num = str('%04d' % files[i][j])
            the_file = 'DSC_' + num + '.jpg'
            if the_file in os.listdir(FROM_WHERE):
                n_exist += 1
                shutil.move(path + the_file, TO + folder)
                time.sleep(0)
                screen.write('\r' + str("%02d" % (i + 1)) + r'/' + str("%02d" % len(files)) +
                             r'  set(s)：' + str(n_exist) + ' of ' + str(len(files[i])) + r' moved')
            if n_exist == 0:
                screen.write('\r' + str("%02d" % (i + 1)) + r'/' + str("%02d" % len(files)) +
                             r'  set(s)：0 of ' + str(len(files[i])) + r' moved')
        screen.flush()

if len(info) != 0:
    mkdir(TO)
    create_name(info)
    print(info)
    legal = 1
    for n in range(0, len(info)):
        if '<' in info.iloc[n, 3] or '>' in info.iloc[n, 3] or '?' in info.iloc[n, 3]:
            legal = 0
            break
        else:
            mkdir(TO + info.iloc[n, 5])
    if legal == 0:
        print('\nany of these characters <>?/\\"*:| is not allowed!\n')
    else:
        print('\nmkdir successful!\n')
        if os.path.exists(FROM_WHERE):
            copy(FROM_WHERE, info, find_file(info))
            print('\n\ncopy successful!')
        else:
            print('please make sure where the photos are!')
else:
    print('no photos to move!')
os.system('pause')
