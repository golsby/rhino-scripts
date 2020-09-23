import re
import subprocess
import os

conf = 'color-scheme.rhc'
version = ''

with open(conf) as f:
    rhc = f.read()

def increment(match):
    global version
    amount = 1
    ver = match.groups(1)[0]
    parts = ver.split('.')
    parts[-1] = str(int(parts[-1]) + amount)
    version = '.'.join(parts)
    return "<SemanticVersion>{0}</SemanticVersion>".format(version)

rhc = re.sub('<SemanticVersion>(.+)</SemanticVersion>', increment, rhc)

with open(conf, 'w') as f:
    f.write(rhc)

print(version)
cwd = os.path.dirname(__file__)
os.chdir(cwd)
full_path = os.path.join(cwd, conf)
print(full_path)
subprocess.call(['RhinoScriptCompiler', full_path])
newfile = 'bin/colorscheme-{0}-rh7-win.yak'.format(version)
os.rename('bin/colorscheme-{0}-any-any.yak'.format(version), newfile)
subprocess.call(['yak', 'push', newfile])