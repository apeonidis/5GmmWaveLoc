import os

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

for n in range(0, 10):
    yFilename = os.path.join(DIR_PATH, 'exported_y_{}.csv'.format(n+1))
    yfile = open(yFilename, 'r');
    
    yFileContent = yfile.read();
    
    yfile.close()

    yfile = open(yFilename, 'w');
    yfile.write(yFileContent.replace("i", "j"));

for n in range(0, 10):
    FFilename = os.path.join(DIR_PATH, 'exported_F_{}.csv'.format(n+1))
    Ffile = open(FFilename, 'r');
    
    FFileContent = Ffile.read();
    
    Ffile.close()

    Ffile = open(FFilename, 'w');
    Ffile.write(FFileContent.replace("i", "j"));
