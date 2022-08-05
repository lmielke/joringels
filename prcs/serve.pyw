import os
import subprocess

template = r'C:\Users\Lars\python_venvs\libraries\joringels\joringels\src\actions\serve.py'
executable = r'C:\Users\Lars\.virtualenvs\joringels-sg8orfNO\Scripts\python.exe'
os.chdir(r'C:\Users\Lars\python_venvs\libraries\joringels')
cmds = ['pipenv', 'run', 'python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2']
subprocess.Popen(cmds, shell=True)

# subprocess.call(['python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2'], shell=True,
#                 executable=executable)