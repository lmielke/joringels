import os
import subprocess

template = os.path.expanduser(r'~/python_venvs/libs/joringels/joringels/src/actions/serve.py')
executable = os.path.expanduser(r'~/.virtualenvs/joringels-RsvOra5c/Scripts/python.exe')
workingdir = os.path.expanduser(r'~/python_venvs/libs/joringels')

os.chdir(workingdir)
# cmds = ['pipenv', 'run', 'python', template, 'serve', '-n', 'digiserver', '-rt']
cmds = ['pipenv', 'run', 'jo', 'serve', '-n', 'digiserver', '-rt']
subprocess.Popen(cmds, shell=True)

# subprocess.call(['python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2'], shell=True,
#                 executable=executable)