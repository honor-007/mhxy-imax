"""
GUI 可复用组件工厂
统一样式、减少重复代码
"""
import ttkbootstrap as tk
from ttkbootstrap.constants import *

# 统一样式常量
FONT = ("Microsoft YaHei UI", 10)
FONT_SMALL = ("Microsoft YaHei UI", 9)
FONT_BOLD = ("Microsoft YaHei UI", 10, "bold")
COMBOBOX_WIDTH = 14
ENTRY_WIDTH = 16
PAD_X = 10
PAD_Y = 5
GROUP_PAD_X = 10
GROUP_PAD_Y = (8, 4)
BUTTON_WIDTH = 10


def create_combobox(parent, row, col, label_text, items, setting_dict, setting_key,
                    font=FONT_SMALL, width=COMBOBOX_WIDTH, padx=PAD_X, pady=PAD_Y):
    """创建带标签的下拉框，自动绑定配置更新"""
    lbl = tk.Label(parent, text=label_text, font=font)
    lbl.grid(row=row, column=col * 2, padx=(padx, 2), pady=pady, sticky='e')

    combo = tk.Combobox(parent, font=font, width=width, state='readonly')
    combo['values'] = items
    default = setting_dict.get(setting_key, items[0] if items else '')
    if default in items:
        combo.current(items.index(default))
    else:
        combo.current(0)

    def on_select(event):
        setting_dict[setting_key] = event.widget.get()

    combo.bind("<<ComboboxSelected>>", on_select)
    combo.grid(row=row, column=col * 2 + 1, padx=(2, padx), pady=pady, sticky='w')
    return combo


def create_entry(parent, row, col, label_text, setting_dict, setting_key,
                 font=FONT_SMALL, width=ENTRY_WIDTH, padx=PAD_X, pady=PAD_Y,
                 state='normal', textvariable=None):
    """创建带标签的输入框，自动绑定配置更新"""
    lbl = tk.Label(parent, text=label_text, font=font)
    lbl.grid(row=row, column=col * 2, padx=(padx, 2), pady=pady, sticky='e')

    kwargs = {'font': font, 'width': width}
    if textvariable is not None:
        kwargs['textvariable'] = textvariable
    entry = tk.Entry(parent, **kwargs)
    if state != 'normal':
        entry.config(state=state)
    elif textvariable is None:
        entry.insert(0, setting_dict.get(setting_key, ''))

    def on_change(event):
        setting_dict[setting_key] = event.widget.get()

    entry.bind("<KeyRelease>", on_change)
    entry.grid(row=row, column=col * 2 + 1, padx=(2, padx), pady=pady, sticky='w')
    return entry


def create_label_frame(parent, text, row=0, col=0, columnspan=1, padx=GROUP_PAD_X, pady=GROUP_PAD_Y, sticky='nsew'):
    """创建分组框"""
    frame = tk.LabelFrame(parent, text=text, padding=(10, 5), bootstyle='primary')
    frame.grid(row=row, column=col, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
    return frame


def create_button(parent, text, command, row=0, col=0, width=BUTTON_WIDTH,
                  bootstyle=OUTLINE, padx=PAD_X, pady=PAD_Y, sticky='', state='normal'):
    """创建按钮"""
    btn = tk.Button(parent, text=text, width=width, command=command, bootstyle=bootstyle)
    btn.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
    if state != 'normal':
        btn.config(state=state)
    return btn


def percent_items(step=5, count=21):
    """生成百分比列表 ['0%', '5%', ..., '100%']"""
    return tuple(f'{i * step}%' for i in range(count))


def fkey_items():
    """生成F键列表"""
    return ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')


def fkey_items_with_none():
    """生成带'无'的F键列表"""
    return ('无',) + fkey_items()


def attack_items():
    """攻击方式列表"""
    return ('无', 'alt+q', 'alt+a', 'alt+d')
