# HELLBOUND

Hellbound is a small, asset-free, Doom-inspired first-person shooter made with
Python 3.13 and pygame. Fight through two levels, clear the demons, and find
the portal to escape.

## Quick start on Windows (no Python required)

1. Open the repository on GitHub and select **Actions**.
2. Open a successful **Build Windows EXE** workflow run.
3. Under **Artifacts**, download **Hellbound-windows**.
4. Extract the downloaded ZIP, then double-click `Hellbound.exe`.

The artifact is produced by the GitHub Actions workflow when a change is
pushed to `main` or `master`, or when the workflow is started manually.

If someone gave you a `Hellbound-Windows.zip` package, extract it and launch
`dist\Hellbound.exe` instead.

## Run from source

To run the Python script instead of the executable, install Python 3.13
(64-bit) from [python.org](https://www.python.org/downloads/), then open
PowerShell in the folder containing `hellbound.py` and `requirements.txt`.
Install pygame and start the game:

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 .\hellbound.py
```

If `py` is not recognized, use the Python 3.13 executable directly:

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

With Python 3.13 installed, run `build_exe.bat` from the project folder. The
standalone game will be created at `dist\Hellbound.exe`. Alternatively, push
the project to GitHub and download the **Hellbound-windows** artifact from a
successful **Build Windows EXE** workflow run.

## Verify the source

To check the maps and ray caster without opening the game:

```powershell
py -3.13 .\hellbound.py --self-test
```
