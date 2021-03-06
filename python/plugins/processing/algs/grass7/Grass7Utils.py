# -*- coding: utf-8 -*-

"""
***************************************************************************
    GrassUtils.py
    ---------------------
    Date                 : February 2015
    Copyright            : (C) 2014-2015 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str
from builtins import object

__author__ = 'Victor Olaya'
__date__ = 'February 2015'
__copyright__ = '(C) 2014-2015, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import stat
import shutil
import subprocess
import os
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog
from processing.tools.system import userFolder, isWindows, isMac, tempFolder, mkdir
from processing.tests.TestData import points


class Grass7Utils(object):

    GRASS_REGION_XMIN = 'GRASS7_REGION_XMIN'
    GRASS_REGION_YMIN = 'GRASS7_REGION_YMIN'
    GRASS_REGION_XMAX = 'GRASS7_REGION_XMAX'
    GRASS_REGION_YMAX = 'GRASS7_REGION_YMAX'
    GRASS_REGION_CELLSIZE = 'GRASS7_REGION_CELLSIZE'
    GRASS_FOLDER = 'GRASS7_FOLDER'
    GRASS_LOG_COMMANDS = 'GRASS7_LOG_COMMANDS'
    GRASS_LOG_CONSOLE = 'GRASS7_LOG_CONSOLE'
    GRASS_HELP_PATH = 'GRASS_HELP_PATH'

    sessionRunning = False
    sessionLayers = {}
    projectionSet = False

    isGrass7Installed = False

    version = None

    @staticmethod
    def grassBatchJobFilename():
        '''This is used in Linux. This is the batch job that we assign to
        GRASS_BATCH_JOB and then call GRASS and let it do the work
        '''
        filename = 'grass7_batch_job.sh'
        batchfile = os.path.join(userFolder(), filename)
        return batchfile

    @staticmethod
    def grassScriptFilename():
        '''This is used in windows. We create a script that initializes
        GRASS and then uses grass commands
        '''
        filename = 'grass7_script.bat'
        filename = os.path.join(userFolder(), filename)
        return filename

    #~ @staticmethod
    #~ def installedVersion():
        #~ out = Grass7Utils.executeGrass7("grass -v")
        #~ # FIXME: I do not know if this should be removed or let the user enter it
        #~ # or something like that... This is just a temporary thing
        #~ return '7.0.0'

    @staticmethod
    def installedVersion(run=False):
        if Grass7Utils.isGrass7Installed and not run:
            return Grass7Utils.version

        if Grass7Utils.grassPath() is None:
            return None

        for command in ["grass73", "grass72", "grass71", "grass70", "grass"]:
            with subprocess.Popen(
                ["{} -v".format(command)],
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            ) as proc:
                try:
                    lines = proc.stdout.readlines()
                    for line in lines:
                        if "GRASS GIS " in line:
                            line = line.split(" ")[-1].strip()
                            if line.startswith("7."):
                                Grass7Utils.version = line
                                Grass7Utils.command = command
                                return Grass7Utils.version
                except:
                    pass

        return None

    @staticmethod
    def grassPath():
        if not isWindows() and not isMac():
            return ''

        folder = ProcessingConfig.getSetting(Grass7Utils.GRASS_FOLDER) or ''
        if not os.path.exists(folder):
            folder = None
        if folder is None:
            if isWindows():
                if "OSGEO4W_ROOT" in os.environ:
                    testfolder = os.path.join(str(os.environ['OSGEO4W_ROOT']), "apps")
                else:
                    testfolder = str(QgsApplication.prefixPath())
                testfolder = os.path.join(testfolder, 'grass')
                if os.path.isdir(testfolder):
                    for subfolder in os.listdir(testfolder):
                        if subfolder.startswith('grass-7'):
                            folder = os.path.join(testfolder, subfolder)
                            break
            else:
                folder = os.path.join(str(QgsApplication.prefixPath()), 'grass7')
                if not os.path.isdir(folder):
                    folder = '/Applications/GRASS-7.0.app/Contents/MacOS'

        return folder or ''

    @staticmethod
    def grassDescriptionPath():
        return os.path.join(os.path.dirname(__file__), 'description')

    @staticmethod
    def createGrass7Script(commands):
        folder = Grass7Utils.grassPath()

        script = Grass7Utils.grassScriptFilename()
        gisrc = os.path.join(userFolder(), 'processing.gisrc7')  # FIXME: use temporary file

        # Temporary gisrc file
        with open(gisrc, 'w') as output:
            location = 'temp_location'
            gisdbase = Grass7Utils.grassDataFolder()

            output.write('GISDBASE: ' + gisdbase + '\n')
            output.write('LOCATION_NAME: ' + location + '\n')
            output.write('MAPSET: PERMANENT \n')
            output.write('GRASS_GUI: text\n')

        with open(script, 'w') as output:
            output.write('set HOME=' + os.path.expanduser('~') + '\n')
            output.write('set GISRC=' + gisrc + '\n')
            output.write('set WINGISBASE=' + folder + '\n')
            output.write('set GISBASE=' + folder + '\n')
            output.write('set GRASS_PROJSHARE=' + os.path.join(folder, 'share', 'proj') + '\n')
            output.write('set GRASS_MESSAGE_FORMAT=plain\n')

            # Replacement code for etc/Init.bat
            output.write('if "%GRASS_ADDON_PATH%"=="" set PATH=%WINGISBASE%\\bin;%WINGISBASE%\\lib;%PATH%\n')
            output.write('if not "%GRASS_ADDON_PATH%"=="" set PATH=%WINGISBASE%\\bin;%WINGISBASE%\\lib;%GRASS_ADDON_PATH%;%PATH%\n')
            output.write('\n')
            output.write('set GRASS_VERSION=' + Grass7Utils.installedVersion() + '\n')
            output.write('if not "%LANG%"=="" goto langset\n')
            output.write('FOR /F "usebackq delims==" %%i IN (`"%WINGISBASE%\\etc\\winlocale"`) DO @set LANG=%%i\n')
            output.write(':langset\n')
            output.write('\n')
            output.write('set PATHEXT=%PATHEXT%;.PY\n')
            output.write('set PYTHONPATH=%PYTHONPATH%;%WINGISBASE%\\etc\\python;%WINGISBASE%\\etc\\wxpython\\n')
            output.write('\n')
            output.write('g.gisenv.exe set="MAPSET=PERMANENT"\n')
            output.write('g.gisenv.exe set="LOCATION=' + location + '"\n')
            output.write('g.gisenv.exe set="LOCATION_NAME=' + location + '"\n')
            output.write('g.gisenv.exe set="GISDBASE=' + gisdbase + '"\n')
            output.write('g.gisenv.exe set="GRASS_GUI=text"\n')
            for command in commands:
                Grass7Utils.writeCommand(output, command)
            output.write('\n')
            output.write('exit\n')

    @staticmethod
    def createGrass7BatchJobFileFromGrass7Commands(commands):
        with open(Grass7Utils.grassBatchJobFilename(), 'w') as fout:
            for command in commands:
                Grass7Utils.writeCommand(fout, command)
            fout.write('exit')

    @staticmethod
    def grassMapsetFolder():
        folder = os.path.join(Grass7Utils.grassDataFolder(), 'temp_location')
        mkdir(folder)
        return folder

    @staticmethod
    def grassDataFolder():
        tempfolder = os.path.join(tempFolder(), 'grassdata')
        mkdir(tempfolder)
        return tempfolder

    @staticmethod
    def createTempMapset():
        '''Creates a temporary location and mapset(s) for GRASS data
        processing. A minimal set of folders and files is created in the
        system's default temporary directory. The settings files are
        written with sane defaults, so GRASS can do its work. The mapset
        projection will be set later, based on the projection of the first
        input image or vector
        '''

        folder = Grass7Utils.grassMapsetFolder()
        mkdir(os.path.join(folder, 'PERMANENT'))
        mkdir(os.path.join(folder, 'PERMANENT', '.tmp'))
        Grass7Utils.writeGrass7Window(os.path.join(folder, 'PERMANENT', 'DEFAULT_WIND'))
        with open(os.path.join(folder, 'PERMANENT', 'MYNAME'), 'w') as outfile:
            outfile.write(
                'QGIS GRASS GIS 7 interface: temporary data processing location.\n')

        Grass7Utils.writeGrass7Window(os.path.join(folder, 'PERMANENT', 'WIND'))
        mkdir(os.path.join(folder, 'PERMANENT', 'sqlite'))
        with open(os.path.join(folder, 'PERMANENT', 'VAR'), 'w') as outfile:
            outfile.write('DB_DRIVER: sqlite\n')
            outfile.write('DB_DATABASE: $GISDBASE/$LOCATION_NAME/$MAPSET/sqlite/sqlite.db\n')

    @staticmethod
    def writeGrass7Window(filename):
        with open(filename, 'w') as out:
            out.write('proj:       0\n')
            out.write('zone:       0\n')
            out.write('north:      1\n')
            out.write('south:      0\n')
            out.write('east:       1\n')
            out.write('west:       0\n')
            out.write('cols:       1\n')
            out.write('rows:       1\n')
            out.write('e-w resol:  1\n')
            out.write('n-s resol:  1\n')
            out.write('top:        1\n')
            out.write('bottom:     0\n')
            out.write('cols3:      1\n')
            out.write('rows3:      1\n')
            out.write('depths:     1\n')
            out.write('e-w resol3: 1\n')
            out.write('n-s resol3: 1\n')
            out.write('t-b resol:  1\n')

    @staticmethod
    def prepareGrass7Execution(commands):
        env = os.environ.copy()

        if isWindows():
            Grass7Utils.createGrass7Script(commands)
            command = ['cmd.exe', '/C ', Grass7Utils.grassScriptFilename()]
        else:
            gisrc = os.path.join(userFolder(), 'processing.gisrc7')
            env['GISRC'] = gisrc
            env['GRASS_MESSAGE_FORMAT'] = 'plain'
            env['GRASS_BATCH_JOB'] = Grass7Utils.grassBatchJobFilename()
            if 'GISBASE' in env:
                del env['GISBASE']
            Grass7Utils.createGrass7BatchJobFileFromGrass7Commands(commands)
            os.chmod(Grass7Utils.grassBatchJobFilename(), stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
            if isMac() and os.path.exists(os.path.join(Grass7Utils.grassPath(), 'grass.sh')):
                command = os.path.join(Grass7Utils.grassPath(), 'grass.sh') + ' ' \
                    + os.path.join(Grass7Utils.grassMapsetFolder(), 'PERMANENT')
            else:
                print("Grass {}".format(Grass7Utils.version))
                command = Grass7Utils.command + ' ' + os.path.join(Grass7Utils.grassMapsetFolder(), 'PERMANENT')

        return command, env

    @staticmethod
    def executeGrass7(commands, feedback, outputCommands=None):
        loglines = []
        loglines.append(Grass7Utils.tr('GRASS GIS 7 execution console output'))
        grassOutDone = False
        command, grassenv = Grass7Utils.prepareGrass7Execution(commands)
        with subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=grassenv
        ) as proc:
            for line in iter(proc.stdout.readline, ''):
                if 'GRASS_INFO_PERCENT' in line:
                    try:
                        feedback.setProgress(int(line[len('GRASS_INFO_PERCENT') + 2:]))
                    except:
                        pass
                else:
                    if 'r.out' in line or 'v.out' in line:
                        grassOutDone = True
                    loglines.append(line)
                    feedback.pushConsoleInfo(line)

        # Some GRASS scripts, like r.mapcalculator or r.fillnulls, call
        # other GRASS scripts during execution. This may override any
        # commands that are still to be executed by the subprocess, which
        # are usually the output ones. If that is the case runs the output
        # commands again.

        if not grassOutDone and outputCommands:
            command, grassenv = Grass7Utils.prepareGrass7Execution(outputCommands)
            with subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=grassenv
            ) as proc:
                for line in iter(proc.stdout.readline, ''):
                    if 'GRASS_INFO_PERCENT' in line:
                        try:
                            feedback.setProgress(int(
                                line[len('GRASS_INFO_PERCENT') + 2:]))
                        except:
                            pass
                    else:
                        loglines.append(line)
                        feedback.pushConsoleInfo(line)

        if ProcessingConfig.getSetting(Grass7Utils.GRASS_LOG_CONSOLE):
            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)

    # GRASS session is used to hold the layers already exported or
    # produced in GRASS between multiple calls to GRASS algorithms.
    # This way they don't have to be loaded multiple times and
    # following algorithms can use the results of the previous ones.
    # Starting a session just involves creating the temp mapset
    # structure
    @staticmethod
    def startGrass7Session():
        if not Grass7Utils.sessionRunning:
            Grass7Utils.createTempMapset()
            Grass7Utils.sessionRunning = True

    # End session by removing the temporary GRASS mapset and all
    # the layers.
    @staticmethod
    def endGrass7Session():
        shutil.rmtree(Grass7Utils.grassMapsetFolder(), True)
        Grass7Utils.sessionRunning = False
        Grass7Utils.sessionLayers = {}
        Grass7Utils.projectionSet = False

    @staticmethod
    def getSessionLayers():
        return Grass7Utils.sessionLayers

    @staticmethod
    def addSessionLayers(exportedLayers):
        Grass7Utils.sessionLayers = dict(
            list(Grass7Utils.sessionLayers.items())
            + list(exportedLayers.items()))

    @staticmethod
    def checkGrass7IsInstalled(ignorePreviousState=False):
        if isWindows():
            path = Grass7Utils.grassPath()
            if path == '':
                return Grass7Utils.tr(
                    'GRASS GIS 7 folder is not configured. Please configure '
                    'it before running GRASS GIS 7 algorithms.')
            cmdpath = os.path.join(path, 'bin', 'r.out.gdal.exe')
            if not os.path.exists(cmdpath):
                return Grass7Utils.tr(
                    'The specified GRASS 7 folder "{}" does not contain '
                    'a valid set of GRASS 7 modules.\nPlease, go to the '
                    'Processing settings dialog, and check that the '
                    'GRASS 7\nfolder is correctly configured'.format(os.path.join(path, 'bin')))

        if not ignorePreviousState:
            if Grass7Utils.isGrass7Installed:
                return
        try:
            from processing import runalg
            result = runalg(
                'grass7:v.voronoi',
                points(),
                False,
                False,
                None,
                -1,
                0.0001,
                0,
                None,
            )
            if not os.path.exists(result['output']):
                return Grass7Utils.tr(
                    'It seems that GRASS GIS 7 is not correctly installed and '
                    'configured in your system.\nPlease install it before '
                    'running GRASS GIS 7 algorithms.')
        except:
            return Grass7Utils.tr(
                'Error while checking GRASS GIS 7 installation. GRASS GIS 7 '
                'might not be correctly configured.\n')

        Grass7Utils.isGrass7Installed = True

    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'Grass7Utils'
        return QCoreApplication.translate(context, string)

    @staticmethod
    def writeCommand(output, command):
        try:
            # Python 2
            output.write(command.encode('utf8') + '\n')
        except TypeError:
            # Python 3
            output.write(command + '\n')

    @staticmethod
    def grassHelpPath():
        helpPath = ProcessingConfig.getSetting(Grass7Utils.GRASS_HELP_PATH)

        if helpPath is None:
            if isWindows():
                localPath = os.path.join(Grass7Utils.grassPath(), 'docs/html')
                if os.path.exists(localPath):
                    helpPath = os.path.abspath(localPath)
            elif isMac():
                localPath = '/Applications/GRASS-7.0.app/Contents/MacOS/docs/html'
                if os.path.exists(localPath):
                    helpPath = os.path.abspath(localPath)
            else:
                searchPaths = ['/usr/share/doc/grass-doc/html',
                               '/opt/grass/docs/html',
                               '/usr/share/doc/grass/docs/html']
                for path in searchPaths:
                    if os.path.exists(path):
                        helpPath = os.path.abspath(path)
                        break

        return helpPath if helpPath is not None else 'http://grass.osgeo.org/{}/manuals/'.format(Grass7Utils.command)
