# -*- coding: utf-8 -*-
import win32com
import win32com.client
from time import sleep

class VideoReDo(object):
    """VideoRedo"""
    vr = None
    def __init__(self):
        self.vrs = win32com.client.Dispatch("VideoReDo.VideoReDoSilent")
        self.vr = self.vrs.VRDInterface

    def FileOpenBatch(self, string):
        return self.vr.FileOpenBatch(string)

    def FileSaveAs(self, string):
        return self.vr.FileSaveAs(string)

    def FileSaveAsEx(self, string, type):
        return self.vr.FileSaveAsEx(string, type)

    def FileSaveProfile(self, string, profile):
        return self.vr.FileSaveProfile(string, profile)

    def IsOutputInProgress(self):
        return self.vr.IsOutputInProgress

    def OpenedFilename(self):
        return self.vr.OpenedFilename

def RepairVideo(source, target):
    vr = VideoReDo()
    vr.FileOpenBatch(source)

    vr.FileSaveProfile(target, "MPEG2 Transport Stream")
	
    sleep(10)

    while (vr.IsOutputInProgress()):
        sleep(5)

    return True