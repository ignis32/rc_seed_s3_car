[app]
# (str) Title of your application
title = Rover Mission Control

# (str) Package name
package.name = rovermissioncontrol

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code directory where the main.py file is located
source.dir = .

# (list) Source file extensions to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to include (leave empty to include all the files)
# source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (leave empty to not exclude anything)
# source.exclude_exts = spec

# (list) List of exclusions using pattern matching
# source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) List of requirements to install (python package, kivy, etc.)
requirements = python3, kivy, requests, pillow, numpy, opencv, pygame, android

# (list) Garden requirements
# garden_requirements =

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = landscape

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Android API to use
android.api = 28

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
# android.sdk =

# (int) Android NDK version to use
android.ndk = 17c
