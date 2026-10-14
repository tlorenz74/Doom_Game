# HELLBOUND

Hellbound is a small, asset-free, Doom-inspired first-person shooter made with
Python 3.13 and pygame. Fight through two levels, clear the demons, and find
the portal to escape.

## Run from PowerShell

From this folder, install the dependency and start the game:

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 .\hellbound.py
```

If the Python launcher (`py`) is unavailable, use the Python 3.13 executable
directly:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -m pip install -r .\requirements.txt
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" .\hellbound.py
```

## Controls

- **WASD / arrow keys:** move
- **Mouse:** look around
- **Left click / Space:** fire
- **Shift:** run
- **Tab:** toggle minimap
- **Esc:** pause or resume
- **R:** restart after winning or dying
- **Q:** quit from pause or end screen

Clear the enemies in each level to open its exit portal.

## Build the Windows executable

With Python 3.13 installed, run `build_exe.bat`. The standalone game will be
created at `dist\Hellbound.exe`. The GitHub Actions workflow also builds this
executable for Python 3.13 and uploads it as the `Hellbound-windows` artifact.

To check the maps and ray caster without starting the game:

```powershell
py -3.13 .\hellbound.py --self-test
```
