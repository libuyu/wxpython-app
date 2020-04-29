import wx
import wx.adv
#import win32gui, win32con
#import ctypes
from pynput import keyboard
        

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class CustomTaskBarIcon(wx.adv.TaskBarIcon):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, frame):
        """Constructor"""
        super().__init__()
        self.frame = frame

        img = wx.Image("hand_only.png", wx.BITMAP_TYPE_ANY).Scale(24, 24)
        bmp = wx.Bitmap(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)
        self.SetIcon(self.icon, "Restore")

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Hand Mode (Ctrl+Shift+A)', self.on_hand)
        create_menu_item(menu, 'Pen Mode (Ctrl+Shift+S)', self.on_pen)
        create_menu_item(menu, 'Disable (Ctrl+Shift+D)', self.off)
        menu.AppendSeparator()
        create_menu_item(menu, 'Zoom In (Ctrl+Shift+Z)', self.zoom_in)
        create_menu_item(menu, 'Zoom Out (Ctrl+Shift+X)', self.zoom_out)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu
 
    def on_hand(self, evt):
        self.frame.set_hand()

    def on_pen(self, evt):
        self.frame.set_pen()

    def off(self, evt):
        self.frame.disable()

    def zoom_in(self, evt):
        self.frame.zoom_in()

    def zoom_out(self, evt):
        self.frame.zoom_out()

    def on_exit(self, event):
        #ctypes.windll.user32.SetSystemCursor(self.frame.cur_origin, 32512)
        self.frame.Close()
        wx.CallAfter(self.Destroy)

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, style=wx.FRAME_SHAPED | wx.STAY_ON_TOP)
        self.tbIcon = CustomTaskBarIcon(self)
        self.img_pen = wx.Image('hand_pen.png')
        self.img_hand = wx.Image('hand_only.png')
        self.img_pen.ConvertAlphaToMask()
        self.img_hand.ConvertAlphaToMask()
        self.w, self.h = self.img_pen.GetSize()
        self.hand = wx.StaticBitmap(self, -1, wx.Bitmap(self.img_hand))
        # self.cur_blank = win32gui.LoadImage(0, 'cur.cur', 
        #            win32con.IMAGE_CURSOR, 0, 0, win32con.LR_LOADFROMFILE)
        # cur_old = win32gui.LoadImage(0, 32512, win32con.IMAGE_CURSOR, 0, 0, win32con.LR_SHARED )
        # self.cur_origin = ctypes.windll.user32.CopyImage(cur_old, win32con.IMAGE_CURSOR, 
        #                     0, 0, win32con.LR_COPYFROMRESOURCE)
        self.SetTransparent(0)
        self.mode = 'hand'
        self.draw()
        self.hotkeys = HotKey(self)
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEAVE_WINDOW, self.hide_cursor)
        #self.Bind(wx.EVT_KEY_DOWN, self.control)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Show()
        self.move()

    def onClose(self, evt):
        """
        Destroy the taskbar icon and the frame
        """
        #ctypes.windll.user32.SetSystemCursor(self.cur_origin, 32512)
        #hotkeys.join()  # remove if main thread is polling self.keys
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def OnPaint(self, evt):
        bitmap = wx.Bitmap(self.img)
        r = wx.Region(bitmap)
        self.SetShape(r)
        self.SetSize(self.img.GetSize())
        self.hand = wx.StaticBitmap(self, -1, bitmap)

    def draw(self):
        #import ipdb; ipdb.set_trace()
        if self.mode == 'none':
            return
        elif self.mode == 'hand':
            img = self.img_hand.Scale(self.w, self.h)
        elif self.mode == 'pen':
            img = self.img_pen.Scale(self.w, self.h)
        self.bitmap = wx.Bitmap(img)
        r = wx.Region(self.bitmap)
        self.SetShape(r)
        self.SetSize(img.GetSize())
        self.hand.SetBitmap(self.bitmap)
        #self.hand.Hide()

    def disable(self):
        self.mode = 'none'
        self.SetTransparent(0)
        #ctypes.windll.user32.SetSystemCursor(self.cur_origin, 32512)

    def set_pen(self):
        self.mode = 'pen'
        self.SetTransparent(255)
        #ctypes.windll.user32.SetSystemCursor(self.cur_blank, 32512)
        self.draw()

    def set_hand(self):
        self.mode = 'hand'
        self.SetTransparent(255)
        #ctypes.windll.user32.SetSystemCursor(self.cur_blank, 32512)
        self.draw()

    def zoom_in(self):
        self.w = int(self.w * 1.1)
        self.h = int(self.h * 1.1)
        self.draw()

    def zoom_out(self):
        self.w = int(self.w * 0.9)
        self.h = int(self.h * 0.9)
        self.draw()

    def control(self, evt):
        keycode = evt.GetKeyCode()
        if evt.ControlDown() and evt.ShiftDown() and 64 < keycode < 123:
            char = chr(keycode)
            #print(char)
            if char == 'A': # hand
                self.set_hand()
            elif char == 'S': # pen
                self.set_pen()
            elif char == 'D': # disable
                self.disable()
            elif char == 'Z': # zoom in
                self.zoom_in()
            elif char == 'X': # zoom out
                self.zoom_out()

    def hide_cursor(self, evt):
        cursor = wx.Cursor(wx.CURSOR_BLANK)
        self.SetCursor(cursor)

    def move(self):
        m_pos = wx.GetMousePosition()
        #c_pos = win32gui.GetCaretPos()
        #print(m_pos, c_pos)
        
        #offset = 5
        #x = pos[0] - offset if pos[0] - offset > 0 else 0
        #y = pos[1] - offset if pos[1] - offset > 0 else 0
        #print(pos)
        self.Move(m_pos)
        #wx.StaticBitmap(self, 1, self.bitmap)
        wx.CallLater(16, self.move)
        #if self.active:
            #wx.CallLater(16, self.move)


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.frame.Show(True)
        return True


class HotKey():
    def __init__(self, frame):
        self.frame = frame
        self.hotkeys = keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+a': self.on_hand,
            '<ctrl>+<shift>+s': self.on_pen,
            '<ctrl>+<shift>+d': self.off,
            '<ctrl>+<shift>+z': self.zoom_in,
            '<ctrl>+<shift>+x': self.zoom_out})
        self.hotkeys.start()
    
    def on_hand(self):
        self.frame.set_hand()

    def on_pen(self):
        self.frame.set_pen()

    def off(self):
        self.frame.disable()

    def zoom_in(self):
        self.frame.zoom_in()

    def zoom_out(self):
        self.frame.zoom_out()


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()

'''
import wx


class HandFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, style=wx.FRAME_SHAPED|wx.CLIP_CHILDREN)
        self.create_shaped_frame()
        self.Bind(wx.EVT_PAINT, self.paint)        
        self.move()
    
    def create_shaped_frame(self):
        self.png = wx.Bitmap('hand.png', wx.BITMAP_TYPE_PNG)
        mask = wx.Mask(self.png, wx.WHITE)
        self.png.SetMask(mask)
        self.SetClientSize((self.png.GetSize()))
        rgn = wx.Region(self.png, wx.BLACK)
        self.SetShape(rgn)

    def paint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.png, 0, 0, True)

    def move(self):
        pos = wx.GetMousePosition()
        #print(pos)
        self.Move(pos)
        wx.CallLater(20, self.move)


if __name__ == '__main__':
    app = wx.App()
    frame = HandFrame()
    frame.Show()
    app.MainLoop()
'''

'''
MIN_ALPHA = 64
MAX_ALPHA = 255

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.alpha = MAX_ALPHA
        self.SetTitle('Mouse Alpha')
        self.on_timer()
    def on_timer(self):
        x, y, w, h = self.GetRect()
        mx, my = wx.GetMousePosition()
        d1 = max(x - mx, mx - (x + w))
        d2 = max(y - my, my - (y + h))
        alpha = MAX_ALPHA - max(d1, d2)
        alpha = max(alpha, MIN_ALPHA)
        alpha = min(alpha, MAX_ALPHA)
        if alpha != self.alpha:
            self.SetTransparent(alpha)
            self.alpha = alpha
        wx.CallLater(20, self.on_timer)
'''