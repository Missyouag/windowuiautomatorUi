'''
把 windows的 uiautomation 转换成Android UI Autimator Viewer的xml文件 方便解析和查看


'''

from datetime import datetime
import time
import os

import xml.etree.ElementTree as et

from PIL import ImageGrab

from uiautomation.uiautomation import _GetDictKeyName, Control,  ExpandCollapseState, \
      PatternIdNames, \
        RangeValuePattern, ScrollPattern,  TextPattern, TogglePattern, ToggleState, ExpandCollapsePattern,ValuePattern,\
        GridItemPattern, GridPattern, SelectionItemPattern,ScrollItemPattern,LegacyIAccessiblePattern,InvokePattern,\
        SelectionPattern,TextEditPattern,TextPattern2

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

    className = control.ControlTypeName
    # 把Control 名字去掉，对应下面文档
    # https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-controlpatternmapping
    className = className.replace('Control','')
    tree.set('class',  className)
    if control.ClassName:
        tree.set('ClassName', control.ClassName)
    if control.ClassName:    
        tree.set('AutomationId', control.AutomationId)
    tree.set('ControlType', control.ControlTypeName)
    mName = control.Name
    # tree.set('name', mName)
    # tree.set('ControlType', str(control.ControlType))
    
    #  兼容 Android UI Autimator Viewer 显示名称
    tree.set("text",mName)
    tree.set("content-desc","")
    tree.set("index","")
    #  兼容 ===================== 显示名称

    if processId != control.ProcessId:
        tree.set('ProcessId', str(control.ProcessId))

    tree.set('Handle', '0x{0:X}({0})'.format(control.NativeWindowHandle))

    rect = control.BoundingRectangle
    tree.set('bounds', f"[{rect.left},{rect.top}][{ rect.right},{rect.bottom}]")


    supportedPatterns = list(filter(lambda t: t[0], ((control.GetPattern(id_), name) for id_, name in PatternIdNames.items())))
    # tree.set(f'supportedPatterns',str(len(supportedPatterns)))
    patternValue = None
    for pt, name in supportedPatterns:
        name=name.replace("Pattern","")
        if isinstance(pt, ValuePattern) or isinstance(pt, RangeValuePattern):
            if pt.Value and patternValue != pt.Value:
                patternValue = pt.Value
                tree.set(f'{name}',str(pt.Value))
        elif isinstance(pt, TogglePattern):
            tree.set(f'{name}',str(_GetDictKeyName(ToggleState.__dict__, pt.ToggleState)))
        elif isinstance(pt, SelectionItemPattern):
            tree.set(f'{name}',str(pt.IsSelected))
        elif isinstance(pt, ExpandCollapsePattern):
            tree.set(f'{name}',str(_GetDictKeyName(ExpandCollapseState.__dict__, pt.ExpandCollapseState)))
        elif isinstance(pt, ScrollPattern):
            tree.set(f'{name}_HorizontalPercent',str(pt.HorizontalScrollPercent))
            tree.set(f'{name}_VerticalPercent',str(pt.VerticalScrollPercent))
            tree.set(f'{name}_HorizontalSize',str(pt.HorizontalViewSize))
            tree.set(f'{name}_VerticalSize',str(pt.VerticalViewSize))
        elif isinstance(pt, GridPattern):
            tree.set(f'{name}_RowCount',str(pt.RowCount))
            tree.set(f'{name}_ColumnCount',str(pt.ColumnCount))
        elif isinstance(pt, GridItemPattern):
            tree.set(f'{name}_Row',str(pt.Row))
            tree.set(f'{name}_Column',str(pt.Column))
        elif isinstance(pt, TextPattern) :
            tree.set(f'{name}',str(pt.DocumentRange.GetText()))
        elif isinstance(pt, InvokePattern):
            tree.set(f'Invoke',str(True))
        elif isinstance(pt, LegacyIAccessiblePattern ):
            if pt.ChildId:
                tree.set(f'{name}_ChildId',str(pt.ChildId))
            if pt.DefaultAction:
                tree.set(f'{name}_DefaultAction',str(pt.DefaultAction))
            if pt.Description:
                tree.set(f'{name}_Description',str(pt.Description))
            if pt.Help:
                tree.set(f'{name}_Help',str(pt.Help))
            if pt.KeyboardShortcut:
                tree.set(f'{name}_KeyboardShortcut',str(pt.KeyboardShortcut))
            if pt.Name and mName!=pt.Name:
                tree.set(f'{name}_Name',str(pt.Name))
            tree.set(f'{name}_Role',str(pt.Role))
            tree.set(f'{name}_State',str(pt.State))
            if pt.Value and patternValue != pt.Value:
                patternValue = pt.Value
                tree.set(f'{name}_Value',str(pt.Value))
        elif isinstance(pt, TextPattern2):
            # pt.GetActiveComposition()
            tree.set(f'TextPattern2',str(True))
        elif isinstance(pt, TextEditPattern):
            # pt.GetActiveComposition()
            tree.set(f'TextEdit',str(True))
        elif isinstance(pt, ScrollItemPattern):
            tree.set(f'ScrollIntoView',str(True))
        elif isinstance(pt, SelectionPattern):
            tree.set(f'CanSelectMultiple',str(pt.CanSelectMultiple))
            tree.set(f'IsSelectionRequired',str(pt.IsSelectionRequired))
        else :
            tree.set(f'supportedPattern_{name}',str(pt))

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









