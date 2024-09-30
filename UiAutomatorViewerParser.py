'''
把 windows的 uiautomation 转换成Android UI Autimator Viewer的xml文件 方便解析和查看


'''

from datetime import datetime
import time
import os

import xml.etree.ElementTree as et

from PIL import ImageGrab

import uiautomation as auto
from uiautomation.uiautomation import _GetDictKeyName, Control,  ExpandCollapseState, \
      PatternIdNames,WindowControl, \
        RangeValuePattern, ScrollPattern,  TextPattern, TogglePattern, ToggleState, ExpandCollapsePattern,ValuePattern,\
        GridItemPattern, GridPattern, SelectionItemPattern,ScrollItemPattern,LegacyIAccessiblePattern,InvokePattern,\
        SelectionPattern,TextEditPattern,TextPattern2,WindowPattern,TransformPattern,TransformPattern2



#定义文件存储路径
tempdir = 'automator'


# 记录耗时
TimeEcho = True

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

def control2Xml(control: Control,processId = 0,runtimeId = (),filterClass=[]):
    '''
        格式化对应node  参考LogControl
        父线程的processId  如果不相同写入
        filterClass 只取需要子界面 只有一级 
        这里用了ProcessId 同一个进程的多个窗口会全部识别
    '''
    tree = et.Element('node')
    # 没有class ?
    # tree.set('class', control.ClassName)

    className = control.ClassName
    # 把Control 名字去掉，对应下面文档
    # https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-controlpatternmapping
    if not className:
        className = control.ControlTypeName
        className = className.replace('Control','')
    tree.set('class',  className)
    if control.ClassName:
        tree.set('ClassName', control.ClassName)
    if control.AutomationId:    
        tree.set('AutomationId', control.AutomationId)
    tree.set('ControlType', control.ControlTypeName)
    mName = control.Name
    # tree.set('name', mName)
    # tree.set('ControlType', str(control.ControlType))
    
    #  兼容 Android UI Autimator Viewer 显示名称
    tree.set("text",mName)
    tree.set("content-desc","")
    # GetSearchPropertiesStr   和别的属性重复 这里不用
    # {ClassName: 'WeChatMainWndForPC', ControlType: WindowControl}
    # tree.set("content-desc",control.GetSearchPropertiesStr())
    index = ""
    myRuntimeId = control.GetRuntimeId()
    for i in range(len(myRuntimeId)):
        if i >= len(runtimeId)  or runtimeId[i] != myRuntimeId[i]:
            index += f"{myRuntimeId[i]} "
    if index.endswith(" "):
        index = index[:-1]
    tree.set("index",str(index))
    #  兼容 ===================== end

    if TimeEcho:
        tree.set("timeLeft",str(humanTime(time.perf_counter_ns() - dayTimeStartInt)))

    tree.set("runtimeId",str(myRuntimeId))
    if processId != control.ProcessId:
        tree.set('ProcessId', str(control.ProcessId))

    if control.NativeWindowHandle:
        tree.set('Handle', '0x{0:X}({0})'.format(control.NativeWindowHandle))

    rect = control.BoundingRectangle
    tree.set('bounds', f"[{rect.left},{rect.top}][{ rect.right},{rect.bottom}]")


    tree.set("ClickablePoint",str(control.GetClickablePoint()))


    supportedPatterns = list(filter(lambda t: t[0], ((control.GetPattern(id_), name) for id_, name in PatternIdNames.items())))
    # tree.set(f'supportedPatterns',str(len(supportedPatterns)))
    patternValue = None
    for pt, name in supportedPatterns:
        name = name.replace("Pattern","")
        if isinstance(pt, ValuePattern) or isinstance(pt, RangeValuePattern):
            if pt.Value and patternValue != pt.Value:
                patternValue = pt.Value
                tree.set(f'{name}',str(pt.Value))
        elif isinstance(pt, TogglePattern):
            tree.set(f'{name}_State',str(_GetDictKeyName(ToggleState.__dict__, pt.ToggleState)))
        elif isinstance(pt, SelectionItemPattern):
            tree.set(f'{name}_IsSelected',str(pt.IsSelected))
        elif isinstance(pt, ExpandCollapsePattern):
            tree.set(f'{name}_State',str(_GetDictKeyName(ExpandCollapseState.__dict__, pt.ExpandCollapseState)))
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
        elif isinstance(pt, TransformPattern):
            tree.set(f'CanMove',str(pt.CanMove))
            tree.set(f'CanResize',str(pt.CanResize))
            tree.set(f'CanRotate',str(pt.CanRotate))
        elif isinstance(pt, WindowPattern):
            tree.set(f'CanMaximize',str(pt.CanMaximize))
            tree.set(f'CanMinimize',str(pt.CanMinimize))
            tree.set(f'IsTopmost',str(pt.IsTopmost))
            tree.set(f'IsModal',str(pt.IsModal))
            tree.set(f'WindowVisualState',str(_GetDictKeyName(auto.WindowVisualState.__dict__,pt.WindowVisualState)))
            tree.set(f'WindowInteractionState',str(_GetDictKeyName(auto.WindowInteractionState.__dict__,pt.WindowInteractionState)))
        elif isinstance(pt, auto.DragPattern):
            tree.set(f'IsGrabbed',str(pt.IsGrabbed))
            if pt.DropEffect:
                tree.set(f'DropEffect',str(pt.DropEffect))
            if pt.DropEffects:
                tree.set(f'DropEffects',str(pt.DropEffects))
        elif isinstance(pt, SelectionPattern):
            tree.set(f'CanSelectMultiple',str(pt.CanSelectMultiple))
            tree.set(f'IsSelectionRequired',str(pt.IsSelectionRequired))
        else :
            tree.set(f'supportedPattern_{name}',str(pt))

    child = control.GetFirstChildControl()
    needProcessId = []
    while child:
        if len(filterClass) < 1 or child.ProcessId in needProcessId or containStrInlist(child.ClassName,filterClass) >= 0:
            if len(filterClass) > 0:
                needProcessId.append(child.ProcessId)
            tree.append(control2Xml(child,control.ProcessId,myRuntimeId))
        child = child.GetNextSiblingControl()


    return tree


def containStrInlist(content,list):
    i = 0
    while(i<len(list)):
        if list[i] in content:
           return i
        i += 1

    return -1


def save2xml(fileName,control: Control,filterClass=[]):
    '''
    保存到xml文件
    '''
    # ET.parse(file_path)
    tree = et.Element('hierarchy')
    tree.set('rotation', str(1))

    tree.append(control2Xml(control,filterClass=filterClass))


    et.ElementTree(tree).write(f"./{tempdir}/{fileName}.xml",'utf-8')


def parserTime(dayTime:datetime = datetime.now()) -> str:
    '''
    时间转换为可以做文件名的字符串
    '''
    return dayTime.strftime('%Y%m%d_%H%M%S_%f')


def humanTime(ns=0):
    '''
    把时间间隔转换成人类可读的时间
    '''
    totalTime = ns
    unit ='ns'
    if(totalTime > 1000000):
        totalTime /= 1000000
        unit ='ms'
        if totalTime>1000:
            totalTime /= 1000
            unit='s'
            if totalTime > 60:
                totalTime /= 60
                unit='min'
                if totalTime > 60:
                    totalTime /= 60
                    unit='h'
    return f"{totalTime} {unit}"



import time

# 起始时间，统计耗时
dayTimeStartInt = 0

#是否保存文件
needSave2File = True

if __name__ == '__main__':
    seconds = 3    # 等待时间 

    if seconds > 0:
        print(f"等待窗口...{seconds}s")
        time.sleep(seconds)

    dayTimeStartInt = time.perf_counter_ns()
    # 对应 xml图片名称 同一名称，方便UIautomatorView查看
    fileName = parserTime(datetime.now())
   
    filterClass=[]

    # 这个是全部内容 内容太多有点卡
    control = auto.GetRootControl()
    #这个筛选出所有微信窗口
    filterClass.append("WeChatMainWndForPC") #主窗口
    
    # WeChatMainWndForPC 下面的子view 错误示范
    # filterClass.append("ChatWnd") #聊天副窗口
    # filterClass.append("SessionChatRoomDetailWnd") #聊天室详情
    # filterClass.append("ChatContactMenu") #聊天@某人菜单
    # filterClass.append("ChatRecordWnd") #消息记录/合并消息
    # filterClass.append("SelectContactWnd") #转发消息选择联系人
    # filterClass.append("WeUIDialog") #接收好友请求
    # filterClass.append("ContactManagerWindow") #联系人管理



    # 这个是聚焦的 仅为一个控件...
    # control = auto.GetFocusedControl()

    # 当前在最前端的View
    # control = auto.GetForegroundControl()


    #微信客户端
    # control = WindowControl(searchDepth=1,ClassName="WeChatMainWndForPC")
    

    #---------------windows11 --------------------------------------
    #  windows11 桌面 桌面图标
    # control  = auto.PaneControl(ClassName="WorkerW") 
    # windows11 任务栏
    # control  = auto.PaneControl(ClassName="Shell_TrayWnd") 
    # if control.Exists(0, 0):
    #     # 尝试点击任务栏微信图标
    #     button = auto.ButtonControl(control,ClassName="SystemTray.NormalButton",Name="微信")
    #     if button:
    #        legacy:LegacyIAccessiblePattern = button.GetPattern(auto.PatternId.LegacyIAccessiblePattern)
    #        print(f"点击按钮:{legacy.DoDefaultAction()}")
    #------------------------------------------------------------
    


    # notepad 窗口
    # notepad = WindowControl(searchDepth=1, ClassName='Notepad')
    # if not notepad.Exists(0, 0):
    #     重新打开
    #     import subprocess
    #     subprocess.Popen('notepad.exe')
    #     notepad.Refind()

    if needSave2File:
        # 控件信息保存为xml文件
        print(f"开始转换控件xml!")
        save2xml(fileName,control,filterClass)

        print(f"开始截屏!")
        printScreen(fileName)
        print(f"生成成功:{tempdir}/{fileName}")

    print(f"总耗时:{humanTime(time.perf_counter_ns()-dayTimeStartInt)}")




