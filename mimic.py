#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import optparse
import time
import shutil
import hashlib
import json

global output_file
output_file='.'
global dir_src
dir_src='.'
global dir_dst
dir_dst='.'

def md5sum(fname):
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else:
            fh.seek(0)
            
    m = hashlib.md5()
    if isinstance(fname, basestring) \
            and os.path.exists(fname):
        with open(fname, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    elif fname.__class__.__name__ in ["StringIO", "StringO"] \
            or isinstance(fname, file):
        for chunk in read_chunks(fname):
            m.update(chunk)
    else:
        return ""
    return m.hexdigest()

output_file_name=str()

def manual():
  p = optparse.OptionParser()
  p.add_option('-r', action='store_true', help='generate report')
  p.add_option('-t', action='store_true', help='generate tree')
  p.add_option('-b', action='store_true', help='backup folder')
  p.add_option('-c', action='store_true', help='copy folder, dst will be created and should not exist earlier')
  p.add_option('-f', action='store_true', help='force overwrite')
  p.add_option('-s', dest='dir_src', help='source dir path')
  p.add_option('-d', dest='dir_dst', help='destination dir path')
  p.add_option('-o', dest='output_file', help='output file name')

  while True:
    options, argument = p.parse_args()
    if len(argument) != 0:
      p.error("incorrect input")

    if options.output_file:
      global output_file
      output_file=options.output_file
    if options.dir_src:
      global dir_src
      dir_src=options.dir_src
    if options.dir_dst:
      global dir_dst
      dir_dst=options.dir_dst

    if options.r:
      generate_report()
      break

    if options.t:
      generate_tree()
      break

    elif options.b:
      if options.dir_src and options.dir_dst:
        backup_folder(options.dir_src,options.dir_dst, options.f)
        break

    elif options.c:
      if options.dir_src and options.dir_dst:
        shutil.copytree(options.dir_src,options.dir_dst)
        break

    else:
      user_input = raw_input("usage: mimic [options]:(enter 'q' to stop)")
      if user_input == 'q':
        break
      sys.argv = user_input.split()

def backup_folder(dir_src,dir_dst,force_overwrite=False):

  #backup current work path
  old_path = os.getcwd()

  report_file_name=os.path.join(old_path,'report_%s.txt'%(time.strftime('%Y%m%d%H%M')))
  fh = open(report_file_name, 'w')
  fh.close()

  md5_dict = dict()
  total_file_num = 0
  #change work path
  os.chdir(dir_src)

  for dirpath, dirnames, filenames in os.walk('.'):
    dst_path = os.path.normpath(os.path.join(dir_dst, dirpath))
    if not os.path.exists(dst_path):
      os.mkdir(dst_path)
    for name in filenames:
      total_file_num = total_file_num + 1

      if not os.path.exists(os.path.join(dst_path, name)):
        shutil.copy(os.path.join(dirpath, name), os.path.join(dst_path, name))
        write_to_file(report_file_name, 'COPYED %s'%(os.path.join(dst_path, name))+'\n')
      else:
        #if os.stat(os.path.join(dirpath, name))[6] != os.stat(os.path.join(dst_path, name))[6]:
        if md5sum(os.path.join(dirpath, name)) != md5sum(os.path.join(dst_path, name)):
          if force_overwrite:
            shutil.copy(os.path.join(dirpath, name), os.path.join(dst_path, name))
            write_to_file(report_file_name, 'OVERWRITE %s'%(os.path.join(dst_path, name))+'\n')
          else:
            write_to_file(report_file_name, 'SKIPCOPY %s already exists but not the same'%(os.path.join(dst_path, name))+'\n')

  #restore work path
  os.chdir(old_path)
  print "Total file numbers: %d"%total_file_num

def create_new_file(file_name):
  fh = open(file_name, 'w')
  fh.close()

def write_to_file(file_name, data):

  fh = open(file_name, 'a')
  fh.write(data) 
  fh.close()

def generate_report(path='.'):

  report_file_name='report_%s.txt'%(time.strftime('%Y%m%d%H%M'))
  fh = open(report_file_name, 'w')
  fh.close()

  md5_dict = dict()

  for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
      md5_result = md5sum(os.path.join(dirpath, name))
      write_to_file(report_file_name, '%s '%(md5_result)+os.path.join(dirpath, name)+'\n')
      if not md5_dict.has_key(md5_result):
        md5_dict[md5_result] = 1
      else:
        write_to_file(report_file_name, 'Same file detected in %s, %d'%(os.path.join(dirpath, name), md5_dict[md5_result])+'\n')
        print 'Same file detected in %s, %d'%(os.path.join(dirpath, name), md5_dict[md5_result])
        md5_dict[md5_result] = md5_dict[md5_result] + 1

def generate_tree_recur(path):
  data={}
  for item in os.listdir(path):
    try:
      if os.path.isfile(os.path.join(path, item)):
        data[item]={"md5":md5sum(os.path.join(path, item))}
      if os.path.isdir(os.path.join(path, item)):
        sub_data=generate_tree_recur(os.path.join(path, item))
        data[item]=sub_data
    except Exception,e:  
      print Exception,":",e
  return data

def generate_tree(path='.'):

  if dir_src == '.':
    old_path = os.getcwd()
  else:
    old_path = os.getcwd()
    os.chdir(dir_src)
    path='.'

  if output_file == '.':
    tree_file_name='tree_%s.json'%(time.strftime('%Y%m%d%H%M'))
  else:
    tree_file_name=output_file
  create_new_file(tree_file_name)

  data=generate_tree_recur(path)
  in_json = json.dumps(data,ensure_ascii=False)

  write_to_file(tree_file_name, in_json)

  os.chdir(old_path)

import wx
class myFrame(wx.Frame):
  def __init__(self): 
    wx.Frame.__init__(self, None, -1, 'Mimic', size = (450,200))
    panel = wx.Panel(self)
    #Button
    self.button1 = wx.Button(panel, -1, u'原文件夹', pos = (10,10), size = (80, 20))
    self.Bind(wx.EVT_BUTTON, self.OnButton1Click, self.button1)
    self.button2 = wx.Button(panel, -1, u'目标文件夹', pos = (10,35), size = (80, 20))
    self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)
    self.button3 = wx.Button(panel, -1, u'输出文件名', pos = (10,60), size = (80, 20))
    self.Bind(wx.EVT_BUTTON, self.OnButton3Click, self.button3)
    self.button4 = wx.Button(panel, -1, u'开始', pos = (10,135), size = (80, 20))
    self.Bind(wx.EVT_BUTTON, self.OnButton4Click, self.button4)
    #TextCtrl
    self.textCtrl1 = wx.TextCtrl(panel, -1, '.', (100,10), size = (300, 20))
    self.textCtrl1.SetInsertionPoint(0)
    self.textCtrl2 = wx.TextCtrl(panel, -1, '.', (100,35), size = (300, 20))
    self.textCtrl2.SetInsertionPoint(0)
    self.textCtrl3 = wx.TextCtrl(panel, -1, '.', (100,60), size = (300, 20))
    self.textCtrl3.SetInsertionPoint(0)
    #RadioBox
    list1=['Tree', 'Report']
    self.radioOperation = wx.RadioBox(panel, -1, 'Operation', (10, 85), wx.DefaultSize, list1, 2, wx.RA_SPECIFY_COLS)
  
  def OnButton1Click(self, event):
    dlg = wx.DirDialog(self,u"选择文件夹",style=wx.DD_DEFAULT_STYLE)  
    if dlg.ShowModal() == wx.ID_OK:
        global dir_src
        dir_src = dlg.GetPath()
        self.textCtrl1.SetValue(dir_src)
    dlg.Destroy()

  def OnButton2Click(self, event):
    dlg = wx.DirDialog(self,u"选择文件夹",style=wx.DD_DEFAULT_STYLE)  
    if dlg.ShowModal() == wx.ID_OK:
        global dst_src
        dst_src = dlg.GetPath()
        self.textCtrl2.SetValue(dst_src)
    dlg.Destroy()

  def OnButton3Click(self, event):
    dlg = wx.FileDialog(self,u"选择文件",style=wx.DD_DEFAULT_STYLE)  
    if dlg.ShowModal() == wx.ID_OK:
        global output_file
        output_file = dlg.GetPath()
        self.textCtrl3.SetValue(output_file)
    dlg.Destroy()

  def OnButton4Click(self, event):
    self.button4.Enable(False)
    if self.radioOperation.GetSelection() == 0:
      generate_tree()
    elif self.radioOperation.GetSelection() == 1:
      generate_report()
    self.button4.Enable(True)

class App(wx.App):
  def OnInit(self):
    self.frame = myFrame()
    self.frame.Show()
    return True

if __name__ == "__main__":

  start_time = time.time()
  #manual()
  #print "Used time: %d seconds."%(time.time()-start_time)
  
  app = App()
  app.MainLoop()

  #raw_input('Enter for continue...')

