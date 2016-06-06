<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lang.zh-CN.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor */\n
svgEditor.readLang({\n
\tlang: "zh-CN",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "保存",\n
\t\t"cancel": "取消",\n
\t\t"key_backspace": "退格", \n
\t\t"key_del": "删除", \n
\t\t"key_down": "下", \n
\t\t"key_up": "上", \n
\t\t"more_opts": "更多选项",\n
\t\t"url": "URL",\n
\t\t"width": "宽度",\n
\t\t"height": "高度"\n
\t},\n
\tmisc: {\n
\t\t"powered_by": "版权所有"\n
\t}, \n
\tui: {\n
\t\t"toggle_stroke_tools": "显示/隐藏更式边线工具",\n
\t\t"palette_info": "点击更改填充颜色，按住Shift键单击更改线条颜色",\n
\t\t"zoom_level": "更改缩放级别",\n
\t\t"panel_drag": "左右拖拽调整面板大小"\n
\t},\n
\tproperties: {\n
\t\t"id": "元素ID",\n
\t\t"fill_color": "更改填充颜色",\n
\t\t"stroke_color": "线条的颜色变化",\n
\t\t"stroke_style": "更改线条样式",\n
\t\t"stroke_width": "更改线条宽度",\n
\t\t"pos_x": "更改X坐标",\n
\t\t"pos_y": "更改Y坐标",\n
\t\t"linecap_butt": "顶端样式: 齐平",\n
\t\t"linecap_round": "顶端样式: 圆滑",\n
\t\t"linecap_square": "顶端样式: 方块",\n
\t\t"linejoin_bevel": "连接处: 削平",\n
\t\t"linejoin_miter": "连接处: 直角",\n
\t\t"linejoin_round": "连接处: 圆角",\n
\t\t"angle": "更改旋转角度",\n
\t\t"blur": "更改高斯模糊值",\n
\t\t"opacity": "更改所选条目的不透明度",\n
\t\t"circle_cx": "改变圆的中心X坐标",\n
\t\t"circle_cy": "改变圆的中心Y坐标",\n
\t\t"circle_r": "改变圆的半径",\n
\t\t"ellipse_cx": "改变椭圆的中心X坐标",\n
\t\t"ellipse_cy": "改变椭圆的中心Y坐标",\n
\t\t"ellipse_rx": "改变椭圆的x半径",\n
\t\t"ellipse_ry": "改变椭圆的y半径",\n
\t\t"line_x1": "更改直线起点的x坐标",\n
\t\t"line_x2": "更改直线终点的x坐标",\n
\t\t"line_y1": "更改直线起点的y坐标",\n
\t\t"line_y2": "更改直线终点的y坐标",\n
\t\t"rect_height": "更改矩形的高度",\n
\t\t"rect_width": "更改矩形的宽度",\n
\t\t"corner_radius": "角半径：",\n
\t\t"image_width": "更改图像的宽度",\n
\t\t"image_height": "更改图像的高度",\n
\t\t"image_url": "更改网址",\n
\t\t"node_x": "更改节点的X坐标",\n
\t\t"node_y": "更改节点的Y坐标",\n
\t\t"seg_type": "修改线段类型",\n
\t\t"straight_segments": "直线",\n
\t\t"curve_segments": "曲线",\n
\t\t"text_contents": "更改文本内容",\n
\t\t"font_family": "更改字体样式",\n
\t\t"font_size": "更改字体大小",\n
\t\t"bold": "粗体",\n
\t\t"italic": "斜体"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "主菜单",\n
\t\t"bkgnd_color_opac": "更改背景颜色/不透明",\n
\t\t"connector_no_arrow": "无箭头",\n
\t\t"fitToContent": "适应内容",\n
\t\t"fit_to_all": "适应于所有的内容",\n
\t\t"fit_to_canvas": "适应画布",\n
\t\t"fit_to_layer_content": "适应层内容",\n
\t\t"fit_to_sel": "适应选中内容",\n
\t\t"align_relative_to": "相对对齐 ...",\n
\t\t"relativeTo": "相对于:",\n
\t\t"网页": "网页",\n
\t\t"largest_object": "最大对象",\n
\t\t"selected_objects": "选中的对象",\n
\t\t"smallest_object": "最小的对象",\n
\t\t"new_doc": "新文档",\n
\t\t"open_doc": "打开文档",\n
\t\t"export_img": "导出",\n
\t\t"save_doc": "保存图像",\n
\t\t"import_doc": "导入SVG",\n
\t\t"align_to_page": "对齐元素到页面",\n
\t\t"align_bottom": "底部对齐",\n
\t\t"align_center": "居中对齐",\n
\t\t"align_left": "左对齐",\n
\t\t"align_middle": "水平居中对齐",\n
\t\t"align_right": "右对齐",\n
\t\t"align_top": "顶端对齐",\n
\t\t"mode_select": "选择工具",\n
\t\t"mode_fhpath": "铅笔工具",\n
\t\t"mode_line": "线工具",\n
\t\t"mode_connect": "连接两个对象",\n
\t\t"mode_rect": "矩形",\n
\t\t"mode_square": "正方形",\n
\t\t"mode_fhrect": "自由矩形",\n
\t\t"mode_ellipse": "椭圆",\n
\t\t"mode_circle": "圆形",\n
\t\t"mode_fhellipse": "自由椭圆",\n
\t\t"mode_path": "路径",\n
\t\t"mode_shapelib": "图形库",\n
\t\t"mode_text": "文字工具",\n
\t\t"mode_image": "图像工具",\n
\t\t"mode_zoom": "缩放工具",\n
\t\t"mode_eyedropper": "吸管",\n
\t\t"no_embed": "注意: 根据SVG图像的存储位置，内嵌的位图可能无法显示!",\n
\t\t"undo": "撤消",\n
\t\t"redo": "重做",\n
\t\t"tool_source": "编辑源",\n
\t\t"wireframe_mode": "线条模式",\n
\t\t"toggle_grid": "显示/隐藏 网格",\n
\t\t"clone": "克隆元素",\n
\t\t"del": "删除元素",\n
\t\t"group_elements": "组合元素",\n
\t\t"make_link": "创建超链接",\n
\t\t"set_link_url": "设置链接URL (设置为空以删除)",\n
\t\t"to_path": "转换为路径",\n
\t\t"reorient_path": "调整路径",\n
\t\t"ungroup": "取消组合元素",\n
\t\t"docprops": "文档属性",\n
\t\t"imagelib": "图像库",\n
\t\t"move_bottom": "移至底部",\n
\t\t"move_top": "移至顶部",\n
\t\t"node_clone": "复制节点",\n
\t\t"node_delete": "删除节点",\n
\t\t"node_link": "连接控制点",\n
\t\t"add_subpath": "添加子路径",\n
\t\t"openclose_path": "打开/关闭 子路径",\n
\t\t"source_save": "保存",\n
\t\t"cut": "剪切",\n
\t\t"copy": "复制",\n
\t\t"paste": "粘贴",\n
\t\t"paste_in_place": "粘贴到原位置",\n
\t\t"delete": "删除",\n
\t\t"group": "组合",\n
\t\t"move_front": "移至顶部",\n
\t\t"move_up": "向上移动",\n
\t\t"move_down": "向下移动",\n
\t\t"move_back": "移至底部"\n
\t},\n
\tlayers: {\n
\t\t"layer":"图层",\n
\t\t"layers": "图层",\n
\t\t"del": "删除图层",\n
\t\t"move_down": "向下移动图层",\n
\t\t"new": "新建图层",\n
\t\t"rename": "重命名图层",\n
\t\t"move_up": "向上移动图层",\n
\t\t"dupe": "复制图层",\n
\t\t"merge_down": "向下合并",\n
\t\t"merge_all": "全部合并",\n
\t\t"move_elems_to": "移动元素至:",\n
\t\t"move_selected": "移动元素至另一个图层"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "图像属性",\n
\t\t"doc_title": "标题",\n
\t\t"doc_dims": "画布大小",\n
\t\t"included_images": "包含图像",\n
\t\t"image_opt_embed": "嵌入数据 (本地文件)",\n
\t\t"image_opt_ref": "Use file reference",\n
\t\t"editor_prefs": "编辑器首选项",\n
\t\t"icon_size": "图标大小",\n
\t\t"language": "语言",\n
\t\t"background": "编辑器背景",\n
\t\t"editor_img_url": "图像 URL",\n
\t\t"editor_bg_note": "注意: 背景不会保存在图像中.",\n
\t\t"icon_large": "大",\n
\t\t"icon_medium": "中",\n
\t\t"icon_small": "小",\n
\t\t"icon_xlarge": "特大",\n
\t\t"select_predefined": "选择预定义:",\n
\t\t"units_and_rulers": "单位 & 标尺",\n
\t\t"show_rulers": "显示标尺",\n
\t\t"base_unit": "基本单位:",\n
\t\t"grid": "网格",\n
\t\t"snapping_onoff": "吸附开/关",\n
\t\t"snapping_stepsize": "吸附步长:",\n
\t\t"grid_color": "网格颜色"\n
\t},\n
\tshape_cats: {\n
\t\t"basic": "常规",\n
\t\t"object": "对象",\n
\t\t"symbol": "符号",\n
\t\t"arrow": "箭头",\n
\t\t"flowchart": "流程图",\n
\t\t"animal": "动物",\n
\t\t"game": "纸牌 & 棋子",\n
\t\t"dialog_balloon": "信息气球",\n
\t\t"electronics": "电力元件",\n
\t\t"math": "数学符号",\n
\t\t"music": "音乐符号",\n
\t\t"misc": "杂项",\n
\t\t"raphael_1": "常用图标1",\n
\t\t"raphael_2": "常用图标2"\n
\t},\n
\timagelib: {\n
\t\t"select_lib": "选择一个图像库",\n
\t\t"show_list": "显示库列表",\n
\t\t"import_single": "单个导入",\n
\t\t"import_multi": "批量导入",\n
\t\t"open": "打开一个新文档"\n
\t},\n
\tnotification: {\n
\t\t"invalidAttrValGiven":"无效的参数",\n
\t\t"noContentToFitTo":"无可适应的内容",\n
\t\t"dupeLayerName":"已存在同名的图层!",\n
\t\t"enterUniqueLayerName":"请输入一个唯一的图层名称",\n
\t\t"enterNewLayerName":"请输入新的图层名称",\n
\t\t"layerHasThatName":"图层已经采用了该名称",\n
\t\t"QmoveElemsToLayer":"您确定移动所选元素到图层\'%s\'吗?",\n
\t\t"QwantToClear":"您希望清除当前绘制的所有图形吗?\\n该操作将无法撤消!",\n
\t\t"QwantToOpen":"您希望打开一个新文档吗?\\n该操作将无法撤消!",\n
\t\t"QerrorsRevertToSource":"SVG文件解析错误.\\n是否还原到最初的SVG文件?",\n
\t\t"QignoreSourceChanges":"忽略对SVG文件所作的更改么?",\n
\t\t"featNotSupported":"不支持该功能",\n
\t\t"enterNewImgURL":"请输入新图像的URLL",\n
\t\t"defsFailOnSave": "注意: 由于您所使用的浏览器存在缺陷, 该图像无法正确显示 (不支持渐变或相关元素). 修复该缺陷后可正确显示.",\n
\t\t"loadingImage":"正在加载图像, 请稍候...",\n
\t\t"saveFromBrowser": "选择浏览器中的 \\"另存为...\\" 将该图像保存为 %s 文件.",\n
\t\t"noteTheseIssues": "同时注意以下几点: ",\n
\t\t"unsavedChanges": "存在未保存的修改.",\n
\t\t"enterNewLinkURL": "输入新建链接的URL地址",\n
\t\t"errorLoadingSVG": "错误: 无法加载SVG数据",\n
\t\t"URLloadFail": "无法从URL中加载",\n
\t\t"retrieving": "检索 \\"%s\\"..."\n
\t},\n
\tconfirmSetStorage: {\n
\t\tmessage: "By default and where supported, SVG-Edit can store your editor "+\n
\t\t"preferences and SVG content locally on your machine so you do not "+\n
\t\t"need to add these back each time you load SVG-Edit. If, for privacy "+\n
\t\t"reasons, you do not wish to store this information on your machine, "+\n
\t\t"you can change away from the default option below.",\n
\t\tstoragePrefsAndContent: "Store preferences and SVG content locally",\n
\t\tstoragePrefsOnly: "Only store preferences locally",\n
\t\tstoragePrefs: "Store preferences locally",\n
\t\tstorageNoPrefsOrContent: "Do not store my preferences or SVG content locally",\n
\t\tstorageNoPrefs: "Do not store my preferences locally",\n
\t\trememberLabel: "Remember this choice?",\n
\t\trememberTooltip: "If you choose to opt out of storage while remembering this choice, the URL will change so as to avoid asking again."\n
\t}\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>8927</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
