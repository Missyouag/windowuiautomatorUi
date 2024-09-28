'''
把 windows的 uiautomation 转换成Android UI Autimator Viewer的xml文件 方便解析和查看


'''

from datetime import datetime
import time
import os

import xml.etree.ElementTree as et

from PIL import ImageGrab

from uiautomation.uiautomation import _GetDictKeyName, Control, ExpandCollapsePattern, ExpandCollapseState, GridItemPattern, GridPattern, PatternIdNames, RangeValuePattern, ScrollPattern, SelectionItemPattern, TextPattern, TogglePattern, ToggleState, ValuePattern

#定义文件存储路径
tempdir = 'automator'

def printScreen(screenName:str='screenshot'):
    '''
    获取整个屏幕的截图
    screenName保存到{tempdir} 的名字
    '''
    # 获取整个屏幕的截图
    screenshot = ImageGrab.grab()

    if(not os.path.exists(f"./{tempdir}")):
        os.makedirs(f"./{tempdir}",True)
    # 保存截图为文件
    screenshot.save(f"./{tempdir}/{screenName}.png")
    # 显示截图
    # screenshot.show()


def control2Xml(control: Control,processId = 0):
    '''
        格式化对应node  参考LogControl
        父线程的processId  如果不相同写入

    '''
    tree = et.Element('node')
    # 没有class ?
    # tree.set('class', control.ClassName)
    tree.set('class',  control.ControlTypeName)
    tree.set('ClassName', control.ClassName)
    tree.set('AutomationId', control.AutomationId)
    # tree.set('ControlType', control.ControlTypeName)
    tree.set('name', control.Name)
    # tree.set('ControlType', str(control.ControlType))
    
    #  兼容 Android UI Autimator Viewer 显示名称
    tree.set("text","")
    tree.set("content-desc","")
    tree.set("index","")
    #  兼容 ===================== 显示名称

    if processId != control.ProcessId:
        tree.set('ProcessId', str(control.ProcessId))

    tree.set('Handle', '0x{0:X}({0})'.format(control.NativeWindowHandle))

    rect = control.BoundingRectangle
    tree.set('bounds', f"[{rect.left},{rect.top}][{ rect.right},{rect.bottom}]")


    supportedPatterns = list(filter(lambda t: t[0], ((control.GetPattern(id_), name) for id_, name in PatternIdNames.items())))
    for pt, name in supportedPatterns:
        if isinstance(pt, ValuePattern) or isinstance(pt, RangeValuePattern):
            tree.set(f'{name}',str(pt.Value))
        elif isinstance(pt, TogglePattern):
            tree.set(f'{name}',str(_GetDictKeyName(ToggleState.__dict__, pt.ToggleState)))
        elif isinstance(pt, SelectionItemPattern):
            tree.set(f'{name}',str(pt.IsSelected))
        elif isinstance(pt, ExpandCollapsePattern):
            tree.set(f'{name}',str(_GetDictKeyName(ExpandCollapseState.__dict__, pt.ExpandCollapseState)))
        elif isinstance(pt, ScrollPattern):
            tree.set(f'{name}_HorizontalScrollPercent',str(pt.HorizontalScrollPercent))
            tree.set(f'{name}_VerticalScrollPercent',str(pt.VerticalScrollPercent))
        elif isinstance(pt, GridPattern):
            tree.set(f'{name}_RowCount',str(pt.RowCount))
            tree.set(f'{name}_ColumnCount',str(pt.ColumnCount))
        elif isinstance(pt, GridItemPattern):
            tree.set(f'{name}_Row',str(pt.Row))
            tree.set(f'{name}_Column',str(pt.Column))
        elif isinstance(pt, TextPattern):
            tree.set(f'{name}',str(pt.DocumentRange.GetText()))


    childrens=control.GetChildren()
    for child in childrens:
        tree.append(control2Xml(child,control.ProcessId))


    return tree




def save2xml(fileName,control: Control):
    '''
    保存到xml文件
    '''
    # ET.parse(file_path)
    tree = et.Element('hierarchy')
    tree.set('rotation', str(1))

    tree.append(control2Xml(control))


    et.ElementTree(tree).write(f"./{tempdir}/{fileName}.xml",'utf-8')


def parserTime(dayTime:datetime = datetime.now()) -> str:
    '''
    时间转换为可以做文件名的字符串
    '''
    return dayTime.strftime('%Y%m%d_%H%M%S_%f')

import uiautomation as auto

if __name__ == '__main__':
    seconds = 3    # 等待时间 

    if seconds > 0:
        print(f"等待窗口...{seconds}s")
        time.sleep(seconds)

    # 对应 xml图片名称 同一名称，方便UIautomatorView查看
    fileName = parserTime(datetime.now())

    # 截屏
    printScreen(fileName)
    
    # 这个是全部内容 内容太多有点卡
    # control = auto.GetRootControl()

    # 这个是聚焦的 仅为一个控件...
    # control = auto.GetFocusedControl()

    # 当前在最前端的View
    control = auto.GetForegroundControl()


    save2xml(fileName,control)
   

    print(f"生成成功,{tempdir}/{fileName}")









