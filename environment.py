import sys
import os
from subprocess import Popen

try:
  print("venvs" not in os.listdir())
  if "venvs" not in os.listdir():
    print("Setting Up Virtual Environment")
    os.system("py -m pip install --upgrade pip")
    os.system("py -m pip install --user virtualenv")
    os.system("mkdir venvs")
    print("Created Venv Directory")
    os.chdir(os.getcwd()+"/venvs")
    print(os.getcwd())
    os.system("py -m virtualenv myenv")
except Exception as e:
  print(e)