# -*- coding: utf-8 -*-
import urllib

from django.conf import settings


class UEditorEventHandler(object):
    """ 用来处理UEditor的事件侦听 """

    def on_selectionchange(self):
        return ""

    def on_contentchange(self):
        return ""

    def render(self, editor_id):
        jscode = """
            %(editor)s.addListener('%(event)s', function () {
                %(event_code)s
        });"""
        event_codes = []
        # 列出所有on_打头的方法，然后在ueditor中进行侦听
        events = filter(lambda x: x[0:3] == "on_", dir(self))
        for event in events:
            event_method = getattr(self, event)
            if callable(event_method):
                event_code = event_method()
                if event_code:
                    event_code = event_code % {"editor": editor_id}
                    event_codes.append(jscode % {
                        "editor": editor_id,
                        "event": event[3:],
                        "event_code": event_code
                    })

        return "\n".join(event_codes) if event_codes else ""


class UEditorCommand(object):
    """ 为前端增加按钮，下拉等扩展"""

    def __init__(self, **kwargs):
        self.uiName = kwargs.pop("uiName", "")
        self.index = kwargs.pop("index", 0)
        self.title = kwargs.pop("title", self.uiName)
        self.ajax_url = kwargs.pop("ajax_url", "")

    def render_ui(self, editor):
        """ 创建ueditor的ui扩展对象的js代码，如button,combo等 """
        raise NotImplementedError

    def render_ajax_command(self):
        """ 生成通过ajax调用后端命令的前端ajax代码 """
        if not self.ajax_url:
            return ""

        return u"""
            UE.ajax.request( '%(ajax_url)s', {
                 data: {
                     name: 'ueditor'
                 },
                 onsuccess: function ( xhr ) {%(ajax_success)s},
                 onerror: function ( xhr ){ %(ajax_error)s }
            });
        """ % {
            "ajax_url": self.ajax_url,
            "ajax_success": self.on_execute_ajax_command("success"),
            "ajax_error": self.on_execute_ajax_command("error")
        }

    def render_command(self):
        """ 返回注册命令的js定义 """
        cmd = self.on_execute_command()
        ajax_cmd = self.render_ajax_command()
        queryvalue_command = self.on_execute_query_value_command()
        cmds = []
        if cmd or ajax_cmd:
            cmds.append(u"""execCommand: function() {
                    %(exec_cmd)s
                    %(exec_ajax_cmd)s
                }
            """ % {"exec_cmd": cmd, "exec_ajax_cmd": ajax_cmd},)

        if queryvalue_command:
            cmds.append(u"""queryCommandValue:function(){
                    %s
                }""" % queryvalue_command)
        if cmds:
            return u"""
            editor.registerCommand(uiName, {
                    %s
                });
            """ % ",".join(cmds)
        else:
            return ""

    def render(self, editor_id):
        return u"""
        UE.registerUI("%(uiName)s", function(editor, uiName) {
            %(registerCommand)s
            %(uiObject)s
        },%(index)s,"%(editor)s");
        """ % {
            "registerCommand": self.render_command(),
            "uiName": self.uiName,
            "uiObject": self.render_ui(editor_id),
            "index": self.index,
            "editor": editor_id,
        }

    def on_execute_command(self):
        """ 返回执行Command时的js代码 """
        return ""

    def on_execute_ajax_command(self, state):
        """ 返回执行Command时发起Ajax调用成功与失败的js代码 """
        return ""

    def on_execute_query_value_command(self):
        """" 返回执行QueryvalueCommand时的js代码 """
        return ""


class UEditorButtonCommand(UEditorCommand):

    def __init__(self, **kwargs):
        self.icon = kwargs.pop("icon", "")
        super(UEditorButtonCommand, self).__init__(**kwargs)

    def onClick(self):
        """ 按钮单击js代码，默认执行uiName命令，默认会调用Command """
        return """editor.execCommand(uiName);"""

    def render_ui(self, editor_id):
        """ 创建button的js代码 """
        return """
            var btn = new UE.ui.Button({
                name: uiName,
                title: "%(title)s",
                cssRules: "background-image:url('%(icon)s')!important;",
                onclick: function() {
                    %(onclick)s
                }
            });
            return btn
        """ % {
            "icon": urllib.basejoin(settings.MEDIA_URL, self.icon),
            "onclick": self.onClick(),
            "title": self.title
        }


class UEditorComboCommand(UEditorCommand):

    def __init__(self, **kwargs):
        self.items = kwargs.pop("items", [])
        self.initValue = kwargs.pop("initValue", "")
        super(UEditorComboCommand, self).__init__(**kwargs)

    def get_items(self):
        return self.items

    def onSelect(self):
        return ""

    def render_ui(self, editor_id):
        """ 创建combo的js代码 """
        return """
        var combox = new UE.ui.Combox({
            editor:editor,
            items:%(items)s,
            onselect:function (t, index) {
                %(onselect)s
            },
            title:'%(title)s',
            initValue:'%(initValue)s'
        });
        return combox;
        """ % {
            "title": self.title,
            "items": str(self.get_items()),
            "onselect": self.onSelect(),
            "initValue": self.initValue
        }


class UEditorDialogCommand(UEditorCommand):
    pass
