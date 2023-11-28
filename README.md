# ecm3423

# (Optional) Run in environment

For Mac:

```
python3 -m venv ./venv
source ./venv/bin/activate
```

# Requirements

```
pip3 install -r requirements.txt
```

#### Assimp

This project depends on Assimp, the Assimp library must be installed to your computer in order for this code to run.

To install assimp, go to the [assimp website](https://www.assimp.org/) and follow the installation instructions, Or using the brew package manager:

```
brew install assimp
```

 ***Note**
 If using brew: PyAssimp looks for assimp in specific locations. For the code to work, create a soft link from the brew dylib to `/usr/local/lib`, for example (this will be changed based on where brew installed assimp, use `brew info assimp` to find location):

 ```bash
ln -s /opt/homebrew/Cellar/assimp/5.3.1/lib/libassimp.5.3.0.dylib /usr/local/lib
 ```

# Running

### Make sure all the installation steps are compleate:

If using a venv, activate the venv:

```
source ./venv/bin/activate
```

Make sure the requirements are installed:

```
pip3 install -r requirements.txt
```

Make sure assimp is installed

```
brew install assimp
ln -s /opt/homebrew/Cellar/assimp/5.3.1/lib/libassimp.5.3.0.dylib /usr/local/lib
```

### Finally, Run!

```
python3 city.py
```

# Video Demo Link:

[Video Here]()