from gc import collect
from pglauncher import PGLauncher

# Star launcher
launcher = PGLauncher()
launcher.loop()

# Cleanup
del launcher
collect()

# Start game
import game
